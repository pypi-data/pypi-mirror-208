from __future__ import annotations

import collections.abc
import itertools
import os
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Literal, Mapping, Optional, Sequence, Type, TypeVar, Union, cast, overload
from urllib.parse import urljoin

import pandas as pd
import requests
from pydantic import ValidationError
from pydantic.main import BaseModel
from requests import HTTPError
from requests import JSONDecodeError as RequestsJSONDecodeError

from chalk._reporting.models import BatchReport, BatchReportResponse
from chalk._reporting.progress import ProgressService
from chalk._version import __version__ as chalkpy_version
from chalk.client import ChalkClient, FeatureReference, OnlineQueryResult
from chalk.client.dataset import DatasetImpl, DatasetVersion, dataset_from_response, load_dataset
from chalk.client.exc import (
    ChalkAuthException,
    ChalkBaseException,
    ChalkComputeResolverException,
    ChalkCustomException,
    ChalkDatasetDownloadException,
    ChalkGetBatchReportException,
    ChalkGetDatasetException,
    ChalkOfflineQueryException,
    ChalkOnlineQueryException,
    ChalkRecomputeDatasetException,
    ChalkResolverRunException,
    ChalkUpdateGraphEntityException,
    ChalkWhoAmIException,
    _generic_chalk_exception,
)
from chalk.client.models import (
    ChalkError,
    ComputeResolverOutputRequest,
    ComputeResolverOutputResponse,
    CreateOfflineQueryJobRequest,
    CreateOfflineQueryJobResponse,
    DatasetRecomputeRequest,
    DatasetResponse,
    DatasetRevisionResponse,
    ErrorCode,
    ExchangeCredentialsRequest,
    ExchangeCredentialsResponse,
    FeatureDropRequest,
    FeatureDropResponse,
    FeatureObservationDeletionRequest,
    FeatureObservationDeletionResponse,
    FeatureResult,
    GetOfflineQueryJobResponse,
    OfflineQueryContext,
    OfflineQueryInput,
    OnlineQueryContext,
    OnlineQueryManyRequest,
    OnlineQueryRequest,
    OnlineQueryResponse,
    ResolverRunResponse,
    TriggerResolverRunRequest,
    UpdateGraphEntityResponse,
    WhoAmIResponse,
)
from chalk.config.auth_config import load_token
from chalk.config.project_config import load_project_config
from chalk.features import DataFrame, Feature, FeatureNotFoundException, FeatureWrapper, ensure_feature, unwrap_feature
from chalk.features._encoding.inputs import recursive_encode
from chalk.features.pseudofeatures import CHALK_TS_FEATURE
from chalk.features.tag import BranchId, EnvironmentId
from chalk.utils import notebook
from chalk.utils.constants import __EMPTY, _EMPTY
from chalk.utils.log_with_context import get_logger
from chalk.utils.missing_dependency import missing_dependency_exception

if TYPE_CHECKING:
    import polars as pl

_logger = get_logger(__name__)

T = TypeVar("T")


class _ChalkHTTPException(BaseModel):
    detail: str
    trace: Optional[str]
    errors: Optional[List[ChalkError]] = None


class _ChalkClientConfig(BaseModel):
    name: str
    client_id: str
    client_secret: str
    api_server: str
    query_server: str
    active_environment: Optional[str]
    branch: Optional[BranchId]


class _BranchDeploymentInfo(BaseModel):
    deployment_id: str
    created_at: datetime


class _BranchInfo(BaseModel):
    name: str
    latest_deployment: Optional[str]
    latest_deployment_time: Optional[datetime]
    deployments: List[_BranchDeploymentInfo]


class _BranchMetadataResponse(BaseModel):
    branches: List[_BranchInfo]


def _to_offline_query_input(
    input: Union[Mapping[Union[str, Feature, Any], Any], pd.DataFrame, pl.DataFrame, DataFrame],
    input_times: Union[Sequence[datetime], datetime, None],
) -> OfflineQueryInput:
    try:
        import polars as pl
    except ImportError:
        raise missing_dependency_exception("chalkpy[runtime]")
    if isinstance(input, (DataFrame, pl.DataFrame)):
        input = input.to_pandas()
    if isinstance(input, collections.abc.Mapping):
        input = {str(k): v for (k, v) in input.items()}
    pd_dataframe: pd.DataFrame
    if isinstance(input, pd.DataFrame):
        pd_dataframe = input
    else:
        pd_dataframe = pd.DataFrame(input)

    columns = pd_dataframe.columns
    matrix: List[List[Any]] = pd_dataframe.T.values.tolist()

    columns_fqn = [str(c) for c in (*columns, CHALK_TS_FEATURE)]
    if input_times is None:
        input_times = datetime.now(timezone.utc)
    if isinstance(input_times, datetime):
        input_times = [input_times for _ in range(len(pd_dataframe))]
    local_tz = datetime.now(timezone.utc).astimezone().tzinfo

    input_times = [x.replace(tzinfo=local_tz) if x.tzinfo is None else x for x in input_times]
    input_times = [x.astimezone(timezone.utc) for x in input_times]

    matrix.append([a for a in input_times])

    for col_index, column in enumerate(matrix):
        for row_index, value in enumerate(column):
            try:
                f = Feature.from_root_fqn(columns_fqn[col_index])
            except FeatureNotFoundException:
                # The feature is not in the graph, so passing the value as-is and hoping it's possible
                # to json-serialize it
                encoded_feature = value
            else:
                encoded_feature = f.converter.from_rich_to_json(
                    value,
                    missing_value_strategy="error",
                )

            matrix[col_index][row_index] = encoded_feature

    return OfflineQueryInput(
        columns=columns_fqn,
        values=matrix,
    )


class OnlineQueryResponseImpl(OnlineQueryResult):
    data: List[FeatureResult]
    errors: List[ChalkError]
    warnings: List[str]

    def __init__(
        self,
        data: List[FeatureResult],
        errors: List[ChalkError],
        warnings: List[str],
    ):
        self.data = data
        self.errors = errors
        self.warnings = warnings
        for d in self.data:
            if d.value is not None:
                try:
                    f = Feature.from_root_fqn(d.field)
                except FeatureNotFoundException:
                    self.warnings.append(
                        f"Return data {d.field}:{d.value} cannot be decoded. Attempting to JSON decode"
                    )
                else:
                    d.value = f.converter.from_json_to_rich(d.value)

        self._values = {d.field: d for d in self.data}

    def _df_repr(self):
        if self.errors:
            info = [vars(x) for x in self.errors]
        else:
            info = []
            for x in self.data:
                if isinstance(x.value, pd.DataFrame):
                    info.append({"Feature": x.field, "Value": "No DataFrame Preview"})
                elif isinstance(x.value, Enum):
                    info.append({"Feature": x.field, "Value": x.value.value})
                else:
                    info.append({"Feature": x.field, "Value": x.value})
        return info

    def __repr__(self) -> str:
        return repr(pd.DataFrame(self._df_repr()))

    def __str__(self):
        return str(pd.DataFrame(self._df_repr()))

    def _repr_markdown_(self):
        lines = []
        if len(self.errors) > 0:
            lines.append(f"## {len(self.errors)} Errors")
            lines.append("")
            for e in self.errors:
                nice_code = str(e.code.value).replace("_", " ").capitalize()
                # {str(e.category.value).capitalize()}
                lines.append(
                    f"### {nice_code}{e.feature and f' ({e.feature})' or ''}{e.resolver and f' ({e.resolver})' or ''}"
                )
                lines.append(e.message)
                lines.append("")

                metadata = {
                    "Exception Kind": e.exception and e.exception.kind,
                    "Exception Message": e.exception and e.exception.message,
                    "Stacktrace": e.exception and e.exception.stacktrace,
                }
                metadata = {k: v for k, v in metadata.items() if v is not None}
                for k, v in metadata.items():
                    lines.append(f"*{k}*")
                    lines.append(f"")
                    lines.append(v)

        import polars as pl

        if len(self.data) > 0:
            lines.append("")
            lines.append(f"## Features")
            lines.append("```")
            content = str(pl.DataFrame(self._df_repr()))
            split = content.split("\n")
            main = "\n".join(itertools.chain(split[1:3], split[5:]))
            lines.append(main)
            lines.append("```")

        return "\n".join(lines)

    def get_feature(self, feature: Any) -> Optional[FeatureResult]:
        # Typing `feature` as Any, as the Features will be typed as the underlying datatypes, not as Feature
        return self._values.get(str(feature))

    def get_feature_value(self, feature: Any) -> Optional[Any]:
        # Typing `feature` as Any, as the Features will be typed as the underlying datatypes, not as Feature
        v = self.get_feature(feature)
        return v and v.value


MAGIC_STR = "chalk".encode("utf-8")


class ChalkAPIClientImpl(ChalkClient):
    __name__ = "ChalkClient"
    __qualname__ = "chalk.client.ChalkClient"

    _latest_client: Optional[ChalkAPIClientImpl] = None

    def __repr__(self):
        return f"chalk.client.ChalkClient<{self._config.name}>"

    def __new__(cls, *args: Any, **kwargs: Any) -> ChalkClient:
        obj = object.__new__(ChalkAPIClientImpl)
        obj.__init__(*args, **kwargs)
        return obj

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        environment: Optional[EnvironmentId] = None,
        api_server: Optional[str] = None,
        query_server: Optional[str] = None,
        branch: Optional[BranchId] = None,
        _skip_cache: bool = False,
        session: Optional[requests.Session] = None,
        additional_headers: Optional[Mapping[str, str]] = None,
    ):
        self.session: requests.Session = session or requests.Session()
        token = load_token(
            client_id=client_id,
            client_secret=client_secret,
            active_environment=environment,
            api_server=api_server,
            skip_cache=_skip_cache,
        )
        if token is None:
            raise ChalkAuthException()

        api_server = token.apiServer or "https://api.chalk.ai"
        self._config = _ChalkClientConfig(
            name=token.name or "",
            client_id=token.clientId,
            client_secret=token.clientSecret,
            api_server=api_server,
            query_server=query_server or api_server,
            branch=branch,
            active_environment=token.activeEnvironment,
        )

        self._default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"chalkpy-{chalkpy_version}",
            "X-Chalk-Client-Id": self._config.client_id,
            "X-Chalk-Features-Versioned": "true",
        }
        self._default_headers.update(additional_headers or {})

        self._exchanged_credentials = False
        self._primary_environment = None

        self.__class__._latest_client = self
        if notebook.is_notebook():
            if branch is None:
                self.whoami()
            else:
                self._get_branches()

    def _exchange_credentials(self):
        _logger.debug("Performing a credentials exchange")
        resp = self.session.post(
            url=urljoin(self._config.api_server, f"v1/oauth/token"),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=ExchangeCredentialsRequest(
                client_id=self._config.client_id,
                client_secret=self._config.client_secret,
                grant_type="client_credentials",
            ).dict(),
            timeout=10,
        )
        resp.raise_for_status()
        response_json = resp.json()
        try:
            creds = ExchangeCredentialsResponse(**response_json)
        except ValidationError:
            raise HTTPError(response=resp)
        self._default_headers["Authorization"] = f"Bearer {creds.access_token}"
        self._primary_environment = creds.primary_environment
        self._exchanged_credentials = True

    def _get_headers(
        self,
        environment_override: Optional[str],
        preview_deployment_id: Optional[str],
        branch: Optional[Union[BranchId, __EMPTY]],
    ) -> dict[str, str]:
        x_chalk_env_id = environment_override or self._config.active_environment or self._primary_environment
        headers = dict(self._default_headers)  # shallow copy
        if x_chalk_env_id is not None:
            headers["X-Chalk-Env-Id"] = x_chalk_env_id
        if preview_deployment_id is not None:
            headers["X-Chalk-Preview-Deployment"] = preview_deployment_id

        if branch is _EMPTY:
            pass
        elif branch is not None:
            headers["X-Chalk-Branch-Id"] = branch
        elif self._config.branch is not None:
            headers["X-Chalk-Branch-Id"] = self._config.branch

        return headers

    @staticmethod
    def _raise_if_200_with_errors(response: BaseModel, exception_cls: Type[ChalkBaseException]):
        errors = getattr(response, "errors", None)
        if errors and isinstance(errors, list) and all(isinstance(e, ChalkError) for e in errors):
            errors = cast(List[ChalkError], errors)
            raise exception_cls(errors=errors)

    @staticmethod
    def _raise_http_error(http_error: HTTPError, exception_cls: Type[ChalkBaseException], **exception_kwargs: Any):
        detail = None
        try:
            response_json = http_error.response.json()
            if isinstance(response_json, Mapping):
                detail = response_json.get("detail")
        except RequestsJSONDecodeError:
            pass

        status_code = http_error.response.status_code
        known_error_code = None
        if status_code == 401:
            known_error_code = ErrorCode.UNAUTHENTICATED
        elif status_code == 403:
            known_error_code = ErrorCode.UNAUTHORIZED

        message = (
            f"{status_code} {detail}" if detail else f"Unexpected Chalk server error with status code {status_code}"
        )
        chalk_error = ChalkError(
            code=known_error_code or ErrorCode.INTERNAL_SERVER_ERROR,
            message=message,
        )
        raise exception_cls(errors=[chalk_error], **exception_kwargs)

    def _request(
        self,
        method: str,
        uri: str,
        response: Optional[Type[T]],
        json: Optional[BaseModel],
        environment_override: Optional[str],
        exception_cls: Type[ChalkBaseException],
        preview_deployment_id: Optional[str],
        branch: Optional[Union[BranchId, __EMPTY]],
        data: Optional[bytes] = None,
        api_server_override: Optional[str] = None,
        metadata_request: bool = True,
        extra_headers: Optional[dict[str, str]] = None,
        **exception_kwargs: Any,
    ) -> T:
        if extra_headers is None:
            extra_headers = {}

        # Track whether we already exchanged credentials for this request
        exchanged_credentials = False
        if not self._exchanged_credentials:
            exchanged_credentials = True
            try:
                self._exchange_credentials()
            except HTTPError as e:
                self._raise_http_error(http_error=e, exception_cls=exception_cls, **exception_kwargs)
        headers = self._get_headers(
            environment_override=environment_override,
            preview_deployment_id=preview_deployment_id,
            branch=branch,
        )
        headers.update(extra_headers)
        default_api_server = self._config.api_server if metadata_request else self._config.query_server
        url = urljoin(api_server_override or default_api_server, uri)
        json_body = json and json.dict()
        r = self.session.request(method=method, headers=headers, url=url, json=json_body, data=data)
        if r.status_code in (401, 403) and not exchanged_credentials:
            # It is possible that credentials expired, or that we changed permissions since we last
            # got a token. Exchange them and try again
            self._exchange_credentials()
            r = self.session.request(method=method, headers=headers, url=url, json=json_body, data=data)

        try:
            if r.status_code >= 400:
                try:
                    exception = _ChalkHTTPException.parse_obj(r.json())
                except Exception:
                    r.raise_for_status()
                raise exception_cls(errors=exception.errors, **exception_kwargs)
        except HTTPError as e:
            self._raise_http_error(http_error=e, exception_cls=exception_cls, **exception_kwargs)
        if response is not None:
            return response(**r.json())
        else:
            return r

    def _get_branches(self):
        try:
            branch = self._config.branch
            result = self._request(
                method="GET",
                uri=f"/v1/branches",
                response=_BranchMetadataResponse,
                json=None,
                environment_override=None,
                exception_cls=_generic_chalk_exception("error getting branches"),
                preview_deployment_id=None,
                branch=branch,
                api_server_override=self._get_local_server_override(None),
            )

        except ChalkBaseException as e:
            # If we can't get branches, we can't do anything else
            self._raise_bad_creds_error(errors=e.errors)
        our_branch = next((b for b in result.branches if b.name == branch), None)
        if our_branch is None:
            project_config = load_project_config()
            branch_names = list(reversed(sorted(result.branches, key=lambda b: str(b.latest_deployment_time))))
            limit = 10
            available_branches = "\n".join(f"  - {b.name}" for b in branch_names[:limit])
            if len(branch_names) > limit:
                available_text = f"The {limit} most recently used branches are:"
            else:
                available_text = "Available branches are:"
            raise ChalkCustomException(
                f"""Your client is set up to use a branch '{branch}' that does not exist. {available_text}

{available_branches}

To deploy new features and resolvers in a Jupyter notebook, you must first create a branch from the Chalk CLI.

>>> cd {Path(project_config.local_path).parent} && chalk apply --branch {branch}

Then, you can run this cell again and see your new work! For more docs on applying changes to branches, see:

https://docs.chalk.ai/cli/apply
"""
            )

    def _raise_bad_creds_error(self, errors: Optional[List[ChalkError]] = None):
        exc = ChalkCustomException(
            f"""We weren't able to authenticate you with the Chalk API. Authentication was attempted with the following credentials:

    Client ID:     {self._config.client_id}
    Client Secret: {'*' * len(self._config.client_secret)}
    Branch:        {self._config.branch or ''}
    Environment:   {self._config.active_environment or ''}
    API Server:    {self._config.api_server}
    chalkpy:       v{chalkpy_version}

If these credentials look incorrect to you, try running

>>> chalk login

from the command line from '{os.getcwd()}'. If you are still having trouble, please contact Chalk support.""",
            errors=errors,
        )
        raise exc

    def whoami(self) -> WhoAmIResponse:
        try:
            return self._request(
                method="GET",
                uri=f"/v1/who-am-i",
                response=WhoAmIResponse,
                json=None,
                environment_override=None,
                exception_cls=ChalkWhoAmIException,
                preview_deployment_id=None,
                metadata_request=True,
                branch=None,
            )
        except ChalkBaseException as e:
            self._raise_bad_creds_error(errors=e.errors)

    def upload_features(
        self,
        input: Mapping[FeatureReference, Any],
        branch: Optional[BranchId] = None,
        environment: Optional[EnvironmentId] = None,
        preview_deployment_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        query_name: Optional[str] = None,
        meta: Optional[Mapping[str, str]] = None,
    ) -> Optional[List[ChalkError]]:
        return self.query(
            input=input,
            output=list(input.keys()),
            staleness=None,
            environment=environment,
            preview_deployment_id=preview_deployment_id,
            correlation_id=correlation_id,
            query_name=query_name,
            meta=meta,
        ).errors

    def query(
        self,
        input: Union[Mapping[FeatureReference, Any], Any],
        output: Sequence[FeatureReference],
        staleness: Optional[Mapping[FeatureReference, str]] = None,
        context: Optional[OnlineQueryContext] = None,  # Deprecated.
        environment: Optional[EnvironmentId] = None,
        tags: Optional[List[str]] = None,
        preview_deployment_id: Optional[str] = None,
        branch: Optional[BranchId] = None,
        correlation_id: Optional[str] = None,
        query_name: Optional[str] = None,
        meta: Optional[Mapping[str, str]] = None,
    ) -> OnlineQueryResponseImpl:
        environment = environment or (context and context.environment)
        tags = tags or (context and context.tags)
        encoded_inputs, encoding_warnings = recursive_encode(input)

        outputs: List[str] = [str(feature) for feature in output]

        branch = branch or self._config.branch
        request = OnlineQueryRequest(
            inputs=encoded_inputs,
            outputs=outputs,
            staleness={} if staleness is None else {ensure_feature(k).root_fqn: v for k, v in staleness.items()},
            context=OnlineQueryContext(
                environment=environment,
                tags=tags,
            ),
            deployment_id=preview_deployment_id,
            branch_id=branch,
            correlation_id=correlation_id,
            query_name=query_name,
            meta=meta,
        )

        extra_headers = {}
        if query_name is not None:
            extra_headers["X-Chalk-Query-Name"] = query_name

        resp = self._request(
            method="POST",
            uri="/v1/query/online",
            json=request,
            response=OnlineQueryResponse,
            environment_override=environment,
            exception_cls=ChalkOnlineQueryException,
            preview_deployment_id=preview_deployment_id,
            branch=branch,
            metadata_request=False,
            extra_headers=extra_headers,
        )
        return OnlineQueryResponseImpl(
            data=resp.data,
            errors=resp.errors or [],
            warnings=encoding_warnings,
        )

    def query_many(
        self,
        input: Union[Mapping[FeatureReference, Sequence[Any]], Any],
        output: Sequence[FeatureReference],
        staleness: Optional[Mapping[FeatureReference, str]] = None,
        context: Optional[OnlineQueryContext] = None,  # Deprecated.
        environment: Optional[EnvironmentId] = None,
        tags: Optional[List[str]] = None,
        preview_deployment_id: Optional[str] = None,
        branch: Optional[BranchId] = None,
        correlation_id: Optional[str] = None,
        query_name: Optional[str] = None,
        meta: Optional[Mapping[str, str]] = None,
        use_feather: Optional[bool] = True,
    ) -> OnlineQueryResponseImpl:

        extra_headers = {}
        if query_name is not None:
            extra_headers["X-Chalk-Query-Name"] = query_name

        environment = environment or (context and context.environment)
        tags = tags or (context and context.tags)
        # TODO: We're doing a lame encoding here b/c recursive_encode will treat our lists
        #       as json to serialize.
        # encoded_inputs, encoding_warnings = recursive_encode(input)
        encoded_inputs = {str(k): v for k, v in input.items()}
        outputs: List[str] = [str(feature) for feature in output]
        request = OnlineQueryManyRequest(
            inputs=encoded_inputs,
            outputs=outputs,
            staleness={} if staleness is None else {ensure_feature(k).root_fqn: v for k, v in staleness.items()},
            context=OnlineQueryContext(
                environment=environment,
                tags=tags,
            ),
            deployment_id=preview_deployment_id,
            branch_id=branch,
            correlation_id=correlation_id,
            query_name=query_name,
            meta=meta,
        )

        if use_feather:
            import pyarrow
            import pyarrow.feather as feather

            data = pyarrow.Table.from_pydict(encoded_inputs)
            buffer = BytesIO()
            buffer.write(MAGIC_STR)
            header = request.copy(exclude={"inputs"}).json()
            header_bytes = header.encode("utf-8")
            buffer.write(len(header_bytes).to_bytes(8, byteorder="big"))
            buffer.write(header_bytes)
            pyarrow.feather.write_feather(data, dest=buffer, compression="lz4")

            buffer.seek(0)

            resp = self._request(
                method="POST",
                uri="/v1/query/feather",
                data=buffer.getvalue(),
                json=None,
                response=None,
                environment_override=environment,
                exception_cls=ChalkOnlineQueryException,
                preview_deployment_id=preview_deployment_id,
                branch=branch,
                metadata_request=False,
                extra_headers=extra_headers,
            )

            if resp.headers.get("Content-Type") == "application/octet-stream":
                return pyarrow.feather.read_table(source=BytesIO(resp.content))
            else:
                resp = OnlineQueryResponse(**resp.json())
        else:
            branch = branch or self._config.branch

            resp = self._request(
                method="POST",
                uri="/v1/query_many/online/detailed",
                json=request,
                response=OnlineQueryResponse,
                environment_override=environment,
                exception_cls=ChalkOnlineQueryException,
                preview_deployment_id=preview_deployment_id,
                branch=branch,
                extra_headers=extra_headers,
            )
        return OnlineQueryResponseImpl(
            data=resp.data,
            errors=resp.errors or [],
            # warnings=encoding_warnings, # this seems to be a bogus var
            warnings=[],
        )

    def offline_query(
        self,
        input: Optional[Union[Mapping[FeatureReference, Any], pd.DataFrame, pl.DataFrame, DataFrame]] = None,
        input_times: Union[Sequence[datetime], datetime, None] = None,
        output: Sequence[FeatureReference] = (),
        required_output: Sequence[FeatureReference] = (),
        environment: Optional[EnvironmentId] = None,
        dataset_name: Optional[str] = None,
        branch: Optional[BranchId] = ...,  # distinguished from user explicitly specifying branch=None
        max_samples: Optional[int] = None,
        wait: bool = False,
        show_progress: bool = False,
        recompute_features: Union[bool, List[FeatureReference]] = False,
    ) -> DatasetImpl:
        if branch is Ellipsis:
            branch = self._config.branch
        unbranched = branch is None
        if wait and unbranched:
            raise ChalkOfflineQueryException(
                errors=[
                    ChalkError(
                        code=ErrorCode.INVALID_QUERY,
                        message="Cannot wait for offline query to complete when branch is not specified.",
                    )
                ]
            )

        try:
            import polars as pl
        except ImportError:
            raise missing_dependency_exception("chalkpy[runtime]")
        del pl  # unused

        if len(output) == 0 and len(required_output) == 0:
            raise ValueError("Either 'output' or 'required_output' must be specified.")
        optional_output_root_fqns = [str(f) for f in output]
        required_output_root_fqns = [str(f) for f in required_output]

        if input is None:
            query_input = None
        else:
            query_input = _to_offline_query_input(input, input_times)

        response = self._create_dataset_job(
            optional_output=optional_output_root_fqns,
            required_output=required_output_root_fqns,
            query_input=query_input,
            dataset_name=dataset_name,
            branch=branch,
            context=OfflineQueryContext(environment=environment),
            max_samples=max_samples,
            recompute_features=recompute_features,
        )

        initialized_dataset = dataset_from_response(response, self)

        revision = initialized_dataset.revisions[-1]
        revision._show_progress = show_progress
        # Set as hydrated so that we never call hydration on datasets from unbranched queries.
        revision._hydrated = revision._hydrated or unbranched or (isinstance(wait, float) and wait == 0.0)

        if not wait:
            return initialized_dataset

        revision.wait_for_completion()
        initialized_dataset.is_finished = True
        return initialized_dataset

    def sample(
        self,
        output: Sequence[FeatureReference] = (),
        required_output: Sequence[FeatureReference] = (),
        output_id: bool = False,
        output_ts: bool = False,
        max_samples: Optional[int] = None,
        dataset: Optional[str] = None,
        branch: Optional[BranchId] = None,
        environment: Optional[EnvironmentId] = None,
    ) -> pd.DataFrame:
        try:
            import polars as pl
        except ImportError:
            raise missing_dependency_exception("chalkpy[runtime]")
        context = OfflineQueryContext(environment=environment)
        optional_output_root_fqns = [str(f) for f in output]
        required_output_root_fqns = [str(f) for f in required_output]

        if len(output) == 0 and len(required_output) == 0:
            raise ValueError("Either 'output' or 'required_output' must be specified.")

        response = self._create_and_await_offline_query_job(
            query_input=None,
            optional_output=optional_output_root_fqns,
            required_output=required_output_root_fqns,
            max_samples=max_samples,
            context=context,
            output_id=output_id,
            output_ts=output_ts,
            dataset_name=dataset,
            branch=branch,
            preview_deployment_id=None,
            lazy=False,
        )
        if isinstance(response, pl.LazyFrame):
            response = response.collect()

        return response.to_pandas()

    def get_dataset(
        self,
        dataset_name: str,
        environment: Optional[EnvironmentId] = None,
    ) -> DatasetImpl:
        response: DatasetResponse = self._get_dataset(
            dataset_name=dataset_name,
            environment=environment,
        )
        if response.errors:
            raise ChalkDatasetDownloadException(
                dataset_name=dataset_name,
                errors=response.errors,
            )
        return dataset_from_response(response, self)

    def delete_features(
        self,
        namespace: str,
        features: Optional[List[str]],
        tags: Optional[List[str]],
        primary_keys: List[str],
        environment: Optional[EnvironmentId] = None,
    ) -> FeatureObservationDeletionResponse:
        _logger.debug(
            (
                f"Performing deletion in environment {environment if environment else 'default'} and namespace "
                f"{namespace} with targets that match the following criteria: features={features}, tags={tags}, "
                f"and primary_keys={primary_keys}"
            )
        )
        return self._request(
            method="DELETE",
            uri="/v1/features/rows",
            json=FeatureObservationDeletionRequest(
                namespace=namespace, features=features, tags=tags, primary_keys=primary_keys
            ),
            response=FeatureObservationDeletionResponse,
            environment_override=environment,
            exception_cls=ChalkResolverRunException,
            preview_deployment_id=None,
            branch=None,
        )

    def drop_features(
        self,
        namespace: str,
        features: List[str],
        environment: Optional[EnvironmentId] = None,
    ) -> FeatureDropResponse:
        _logger.debug(
            (
                f"Performing feature drop in environment {environment if environment else 'default'} and namespace "
                f"{namespace} for the following features:{features}."
            )
        )
        return self._request(
            method="DELETE",
            uri="/v1/features/columns",
            json=FeatureDropRequest(namespace=namespace, features=features),
            response=FeatureDropResponse,
            environment_override=environment,
            exception_cls=ChalkResolverRunException,
            preview_deployment_id=None,
            branch=None,
        )

    def trigger_resolver_run(
        self,
        resolver_fqn: str,
        environment: Optional[EnvironmentId] = None,
        preview_deployment_id: Optional[str] = None,
        branch: Optional[BranchId] = None,
    ) -> ResolverRunResponse:
        _logger.debug(f"Triggering resolver {resolver_fqn} to run")
        return self._request(
            method="POST",
            uri="/v1/runs/trigger",
            json=TriggerResolverRunRequest(resolver_fqn=resolver_fqn),
            response=ResolverRunResponse,
            environment_override=environment,
            exception_cls=ChalkResolverRunException,
            preview_deployment_id=preview_deployment_id,
            branch=branch,
        )

    def get_run_status(
        self,
        run_id: str,
        environment: Optional[EnvironmentId] = None,
        preview_deployment_id: Optional[str] = None,
        branch: Optional[BranchId] = None,
    ) -> ResolverRunResponse:
        response = self._request(
            method="GET",
            uri=f"/v1/runs/{run_id}",
            response=ResolverRunResponse,
            json=None,
            environment_override=environment,
            exception_cls=ChalkResolverRunException,
            preview_deployment_id=preview_deployment_id,
            branch=branch,
        )

        return response

    def _create_and_await_offline_query_job(
        self,
        optional_output: List[str],
        required_output: List[str],
        query_input: Optional[OfflineQueryInput],
        max_samples: Optional[int],
        dataset_name: Optional[str],
        branch: Optional[BranchId],
        context: OfflineQueryContext,
        output_id: bool,
        output_ts: bool,
        preview_deployment_id: Optional[str],
        lazy: bool = True,
    ) -> Union[pl.DataFrame, pl.LazyFrame]:
        req = CreateOfflineQueryJobRequest(
            output=optional_output,
            required_output=required_output,
            destination_format="PARQUET",
            input=query_input,
            max_samples=max_samples,
            dataset_name=dataset_name,
            branch=branch,
        )
        response = self._create_offline_query_job(
            request=req,
            context=context,
            preview_deployment_id=preview_deployment_id,
            branch=branch,
        )
        self._raise_if_200_with_errors(response=response, exception_cls=ChalkOfflineQueryException)
        return self._await_offline_query_job(
            job_id=response.job_id,
            outputs=[*optional_output, *required_output],
            lazy=lazy,
            context=context,
            output_id=output_id,
            output_ts=output_ts,
        )

    @overload
    def _await_offline_query_job(
        self,
        job_id: uuid.UUID,
        outputs: List[str],
        lazy: bool,
        context: Optional[OfflineQueryContext],
        output_id: bool,
        output_ts: bool,
        urls_only: Literal[False] = ...,
        branch: Optional[BranchId] = ...,
    ) -> Union[pl.DataFrame, pl.LazyFrame]:
        ...

    @overload
    def _await_offline_query_job(
        self,
        job_id: uuid.UUID,
        outputs: List[str],
        lazy: bool,
        context: Optional[OfflineQueryContext],
        output_id: bool,
        output_ts: bool,
        urls_only: Literal[True],
        branch: Optional[BranchId] = ...,
    ) -> List[str]:
        ...

    def _await_offline_query_job(
        self,
        job_id: uuid.UUID,
        outputs: List[str],
        lazy: bool,
        context: Optional[OfflineQueryContext],
        output_id: bool,
        output_ts: bool,
        urls_only: bool = False,
        branch: Optional[BranchId] = None,
    ) -> Union[pl.DataFrame, pl.LazyFrame, List[str]]:
        while True:
            status = self._get_job_status(job_id=job_id, environment=context and context.environment, branch=branch)
            if status.is_finished:
                break
            time.sleep(0.5)
        if urls_only:
            return status.urls
        return load_dataset(
            uris=status.urls,
            output_features=outputs,
            version=DatasetVersion(status.version),
            output_id=output_id,
            output_ts=output_ts,
            columns=status.columns,
            lazy=lazy,
        )

    def _recompute_dataset(
        self,
        dataset_name: Optional[str],
        dataset_id: Optional[uuid.UUID],
        revision_id: Optional[uuid.UUID],
        features: List[Union[str, Any]],
        branch: BranchId,
        environment: Optional[EnvironmentId],
    ) -> DatasetRevisionResponse:
        request = DatasetRecomputeRequest(
            dataset_name=dataset_name,
            dataset_id=str(dataset_id) if dataset_id is not None else None,
            revision_id=str(revision_id) if revision_id is not None else None,
            features=[str(f) for f in features],
            branch=branch,
        )
        exception_name = str(dataset_name) if dataset_name else str(dataset_id) if dataset_id else None
        return self._request(
            method="POST",
            uri="/v4/dataset/recompute",
            json=request,
            response=DatasetRevisionResponse,
            environment_override=environment,
            exception_cls=ChalkRecomputeDatasetException,
            preview_deployment_id=None,
            branch=branch,
            dataset_name=exception_name,
            api_server_override=self._get_local_server_override(branch),
        )

    def _create_dataset_job(
        self,
        optional_output: List[str],
        required_output: List[str],
        query_input: Optional[OfflineQueryInput],
        max_samples: Optional[int],
        dataset_name: Optional[str],
        branch: Optional[BranchId],
        context: OfflineQueryContext,
        recompute_features: Union[bool, List[FeatureReference]] = False,
    ) -> DatasetResponse:
        if isinstance(recompute_features, list):
            recompute_features = [
                unwrap_feature(f).fqn if isinstance(f, FeatureWrapper) else f for f in recompute_features
            ]
        req = CreateOfflineQueryJobRequest(
            output=optional_output,
            required_output=required_output,
            destination_format="PARQUET",
            input=query_input,
            max_samples=max_samples,
            dataset_name=dataset_name,
            branch=branch,
            recompute_features=recompute_features,
        )
        response = self._create_dataset_request(
            request=req,
            context=context,
            preview_deployment_id=None,
            branch=branch,
        )
        self._raise_if_200_with_errors(response=response, exception_cls=ChalkOfflineQueryException)
        return response

    def compute_resolver_output(
        self,
        input: Union[Mapping[Union[str, Feature], Any], pl.DataFrame, pd.DataFrame, DataFrame],
        input_times: List[datetime],
        resolver: str,
        context: Optional[OfflineQueryContext] = None,
        preview_deployment_id: Optional[str] = None,
        branch: Optional[BranchId] = None,
    ) -> pl.DataFrame:
        try:
            import polars as pl
        except ImportError:
            raise missing_dependency_exception("chalkpy[runtime]")
        if context is None:
            context = OfflineQueryContext()
        query_input = _to_offline_query_input(input, input_times)
        request = ComputeResolverOutputRequest(input=query_input, resolver_fqn=resolver)
        response = self._request(
            method="POST",
            uri="/v1/compute_resolver_output",
            json=request,
            response=ComputeResolverOutputResponse,
            environment_override=context.environment,
            exception_cls=ChalkComputeResolverException,
            preview_deployment_id=preview_deployment_id,
            branch=branch,
        )
        self._raise_if_200_with_errors(response=response, exception_cls=ChalkComputeResolverException)

        while True:
            status = self._get_compute_job_status(
                job_id=response.job_id,
                context=context,
                preview_deployment_id=preview_deployment_id,
                branch=branch,
            )
            if status.is_finished:
                break
            time.sleep(0.5)

        df = load_dataset(
            uris=status.urls,
            version=status.version,
            executor=None,
            columns=status.columns,
        )
        if isinstance(df, pl.LazyFrame):
            df = df.collect()
        return df

    def _get_compute_job_status(
        self,
        job_id: str,
        context: OfflineQueryContext,
        preview_deployment_id: Optional[str],
        branch: Optional[BranchId] = None,
    ) -> GetOfflineQueryJobResponse:
        return self._request(
            method="GET",
            uri=f"/v1/compute_resolver_output/{job_id}",
            response=GetOfflineQueryJobResponse,
            json=None,
            environment_override=context.environment,
            exception_cls=ChalkComputeResolverException,
            preview_deployment_id=preview_deployment_id,
            branch=branch,
        )

    def _create_dataset_request(
        self,
        request: CreateOfflineQueryJobRequest,
        context: OfflineQueryContext,
        preview_deployment_id: Optional[str],
        branch: Optional[BranchId] = None,
    ):
        response = self._request(
            method="POST",
            uri="/v4/offline_query",
            json=request,
            response=DatasetResponse,
            environment_override=context.environment,
            exception_cls=ChalkOfflineQueryException,
            preview_deployment_id=preview_deployment_id,
            branch=branch,
            api_server_override=self._get_local_server_override(branch),
        )
        return response

    def _create_offline_query_job(
        self,
        request: CreateOfflineQueryJobRequest,
        context: OfflineQueryContext,
        preview_deployment_id: Optional[str],
        branch: Optional[BranchId] = None,
    ):
        response = self._request(
            method="POST",
            uri="/v2/offline_query",
            json=request,
            response=CreateOfflineQueryJobResponse,
            environment_override=context.environment,
            exception_cls=ChalkOfflineQueryException,
            preview_deployment_id=preview_deployment_id,
            branch=branch,
        )
        return response

    def _get_job_status(
        self, job_id: uuid.UUID, environment: Optional[EnvironmentId], branch: Optional[BranchId]
    ) -> GetOfflineQueryJobResponse:
        return self._request(
            method="GET",
            uri=f"/v2/offline_query/{job_id}",
            response=GetOfflineQueryJobResponse,
            environment_override=environment,
            json=None,
            exception_cls=ChalkOfflineQueryException,
            preview_deployment_id=None,
            branch=branch,
            api_server_override=self._get_local_server_override(branch),
        )

    def _get_dataset(self, dataset_name: str, environment: Optional[EnvironmentId]) -> DatasetResponse:
        return self._request(
            method="GET",
            uri=f"/v3/offline_query/{dataset_name}",
            response=DatasetResponse,
            environment_override=environment,
            json=None,
            exception_cls=ChalkDatasetDownloadException,
            preview_deployment_id=None,
            branch=None,
            dataset_name=dataset_name,
        )

    def _get_anonymous_dataset(
        self, revision_id: str, environment: Optional[EnvironmentId], branch: Optional[BranchId]
    ) -> DatasetImpl:
        response = self._request(
            method="GET",
            uri=f"/v4/offline_query/{revision_id}",
            response=DatasetResponse,
            environment_override=environment,
            json=None,
            exception_cls=ChalkGetDatasetException,
            revision_id=revision_id,
            preview_deployment_id=None,
            branch=branch,
            api_server_override=self._get_local_server_override(branch),
        )
        return dataset_from_response(response, self)

    def _get_batch_report(self, operation_id: Optional[uuid.UUID]) -> Optional[BatchReport]:
        try:
            response = self._request(
                method="GET",
                uri=f"/v4/offline_query/{operation_id}/status",
                response=BatchReportResponse,
                json=None,
                environment_override=None,
                exception_cls=ChalkGetBatchReportException,
                preview_deployment_id=None,
                branch=_EMPTY,
                operation_id=operation_id,
            )
        except ChalkGetBatchReportException as e:
            if "404" in e.full_message:  # Hack
                return None
            raise e

        return response.report

    def _send_updated_entity(
        self, environment: Optional[EnvironmentId], pickled_entity: bytes
    ) -> UpdateGraphEntityResponse:
        resp = self._request(
            method="POST",
            uri=f"/v1/update_graph_entity",
            response=UpdateGraphEntityResponse,
            json=None,
            data=pickled_entity,
            environment_override=environment,
            exception_cls=ChalkUpdateGraphEntityException,
            preview_deployment_id=None,
            branch=None,
            api_server_override=self._get_local_server_override(None),
        )
        if resp.errors:
            raise ChalkUpdateGraphEntityException(errors=resp.errors)
        return resp

    def _await_operation_completion(
        self, operation_id: uuid.UUID, show_progress: bool = True, caller_method: Optional[str] = None
    ):
        ProgressService(operation_id=operation_id, client=self, caller_method=caller_method).await_operation(
            show_progress=show_progress
        )

    def _get_local_server_override(self, body_branch: Optional[BranchId]) -> Optional[str]:
        branched = body_branch is not None or self._config.branch is not None
        server = self._config.api_server
        is_local = server.startswith("http://localhost") or server.startswith("http://127.0.0.1")

        server_override = None
        if branched and is_local:
            server_override = "http://localhost:1337"

        return server_override
