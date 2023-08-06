from __future__ import annotations

import functools
import warnings
from enum import Enum
from typing import TYPE_CHECKING, Any, Collection, Dict, FrozenSet, List, Mapping, Optional, Sequence, Tuple, Union

import pyarrow as pa

from chalk.features import DataFrame, Feature, FeatureConverter, Features
from chalk.sql._internal.incremental import IncrementalSettings
from chalk.sql.protocols import BaseSQLSourceProtocol
from chalk.utils.missing_dependency import missing_dependency_exception
from chalk.utils.string import normalize_string_for_matching

if TYPE_CHECKING:
    import sqlalchemy.ext.asyncio
    from sqlalchemy.engine import Connection
    from sqlalchemy.sql import Select
    from sqlalchemy.sql.elements import TextClause


class Finalizer(str, Enum):
    ONE_OR_NONE = "OneOrNone"
    ONE = "One"
    FIRST = "First"
    ALL = "All"


def _get_matching_root_fqn(normalized_col_name: str, expected_feature_root_fqns: Collection[str]) -> Optional[str]:
    candidates: List[str] = []
    for x in expected_feature_root_fqns:
        root_fqn_normalized = normalize_string_for_matching(x.lower())
        without_root_ns = normalize_string_for_matching(".".join(x.split(".")[1:]))
        if normalized_col_name == root_fqn_normalized or normalized_col_name == without_root_ns:
            candidates.append(x)
    if len(candidates) == 0:
        return None
    if len(candidates) > 1:
        # We really shouldn't hit this, unless if features are case-sensitive and the user is querying
        # snowflake which is case-insensitive
        raise ValueError(
            (
                f"Column '{normalized_col_name}' was ambiguous which feature it referred to. "
                f"Possible candidates were: {candidates}"
            )
        )
    return candidates[0]


class FinalizedChalkQuery:
    """A query that cannot be further filtered."""

    def __init__(
        self,
        query: Union[Select, TextClause],
        params: Mapping[str, Any],
        finalizer: Finalizer,
        incremental_settings: Optional[IncrementalSettings],
        source: BaseSQLSourceProtocol,
        fields: Mapping[str, Feature],
    ) -> None:
        self._query = query
        self._params = dict(params)
        self._finalizer = finalizer
        self._incremental_settings = incremental_settings
        self._source = source
        self._fields = fields

    @property
    def incremental_settings(self):
        return self._incremental_settings

    @property
    def finalizer(self):
        return self._finalizer

    @property
    def query(self):
        return self._query

    @property
    def source(self):
        return self._source

    @property
    def fields(self):
        return self._fields

    @property
    def params(self):
        return self._params

    def execute(
        self,
        expected_features: Optional[Sequence[Feature]] = None,
        connection: Optional[Any] = None,
    ) -> Union[Features, DataFrame, None]:
        """Actually execute the query to a `DataFrame` or set of features.

        If the finalizer was ONE, ONE_OR_NONE, or FIRST, then a `Features` instance
        is returned. Otherwise, if the `finalizer` is ALL, then a `DataFrame` instance
        is returned.

        Parameters
        ----------
        expected_features
            The list of expected features for the output, as provided by the resovler in which this query is executed.
            If not specified, the column names as returned by the query will be used to determine the output features.
        connection
            Execute the query using the supplied connection. If `None` (default), a new connection will be acquired
            from the underlying source for the query

        Returns
        -------
        DataFrame
            A `DataFrame`, if the `.finalizer` is ALL; otherwise, `Features` set.
            If the finalizer is ONE_OR_NONE or FIRST, then the result may be
            `None` if no row was found
        """

        pa_table = self.execute_to_pyarrow(expected_features, connection)
        return self._pa_table_to_res(pa_table)

    async def async_execute(
        self,
        expected_features: Optional[Sequence[Feature]] = None,
        connection: Optional[Any] = None,
    ) -> Union[Features, DataFrame, None]:
        """Actually execute the query to a `DataFrame` or set of features.

        If the finalizer was ONE, ONE_OR_NONE, or FIRST, then a `Features` instance
        is returned. Otherwise, if the `finalizer` is ALL, then a `DataFrame` instance
        is returned.

        Parameters
        ----------
        expected_features
            The list of expected features for the output, as provided by the resovler in which this query is executed.
            If not specified, the column names as returned by the query will be used to determine the output features.
        connection
            Execute the query using the supplied connection. If `None` (default), a new connection will be acquired
            from the underlying source for the query

        Returns
        -------
        DataFrame
            A `DataFrame`, if the `.finalizer` is ALL; otherwise, `Features` set.
            If the finalizer is ONE_OR_NONE or FIRST, then the result may be
            `None` if no row was found
        """

        pa_table = await self.async_execute_to_pyarrow(expected_features, connection)
        return self._pa_table_to_res(pa_table)

    def _pa_table_to_res(self, pa_table: pa.Table):
        try:
            import polars as pl
        except ImportError:
            raise missing_dependency_exception("chalkpy[runtime]")
        df = pl.from_arrow(pa_table)
        assert isinstance(df, pl.DataFrame)
        res = DataFrame(df)
        if self._finalizer in (Finalizer.ONE_OR_NONE, Finalizer.FIRST) and len(res) == 0:
            return None
        if self._finalizer in (Finalizer.ONE, Finalizer.ONE_OR_NONE, Finalizer.FIRST):
            return res.slice(0, 1).to_features()[0]
        return res

    def _get_col_to_converter(
        self,
        expected_features: Optional[Sequence[Feature]] = None,
    ):
        expected_feature_root_fqns = (
            None if expected_features is None else frozenset(x.root_fqn for x in expected_features)
        )

        def col_to_converters(column_names: List[str]) -> Dict[str, FeatureConverter]:
            # First map the column names to determine the feature fqns
            col_name_mapping = self.get_col_name_mapping(tuple(column_names), expected_feature_root_fqns)
            return {k: Feature.from_root_fqn(v).converter for (k, v) in col_name_mapping.items()}

        return col_to_converters

    def _check_incremental_settings(self):
        if self.incremental_settings is not None:
            # FIXME: Move the incrementalization logic here, so then the `execute` and `execute_to_dataframe`
            # methods can take the hwm timestamp as a paramater, to allow for direct execution
            warnings.warn(
                (
                    "This query specified an incremental configuration, which has not been applied. "
                    "This is likely because the resolver is being executed directly. "
                    "The query will be attempted without any high-water-mark timestamp. "
                    "This will attempt to select all data, "
                    "or if the filters depend on the incremental timestamp, "
                    "will result in a query execution error. "
                )
            )

    def execute_to_pyarrow(
        self,
        expected_features: Optional[Sequence[Feature]] = None,
        connection: Optional[Connection] = None,
    ) -> pa.Table:
        """Actually execute the query, and return a PyArrow table. Unlike :meth:`.execute`, this method will always keep the
        results as a PyArrow table, even if the finalizer implies a singleton results (e.g. ONE, ONE_OR_NONE, or FIRST).

        Parameters
        ----------
        expected_features
            The list of expected features for the output, as provided by the resovler in which this query is executed.
            If not specified, the column names as returned by the query will be used to determine the output features.
        connection
            Execute the query using the supplied connection. If None (the default), then a new connection will be acquired
            from the underlying source for the query

        Returns
        -------
        Table
            A `pa.Table`, even if the result contains 0 or 1 rows.
        """
        self._check_incremental_settings()
        col_to_converters = self._get_col_to_converter(expected_features)

        pa_table = self.source.execute_query(self, col_to_converters, connection)

        return self._postprocess_table(pa_table, expected_features)

    async def async_execute_to_pyarrow(
        self,
        expected_features: Optional[Sequence[Feature]] = None,
        connection: Optional[sqlalchemy.ext.asyncio.AsyncConnection] = None,
    ) -> pa.Table:
        """Actually execute the query, and return a PyArrow table. Unlike :meth:`.execute`, this method will always keep the
        results as a PyArrow table, even if the finalizer implies a singleton results (e.g. ONE, ONE_OR_NONE, or FIRST).

        Parameters
        ----------
        expected_features
            The list of expected features for the output, as provided by the resovler in which this query is executed.
            If not specified, the column names as returned by the query will be used to determine the output features.
        connection
            Execute the query using the supplied connection. If None (the default), then a new connection will be acquired
            from the underlying source for the query

        Returns
        -------
        Table
            A `pa.Table`, even if the result contains 0 or 1 rows.
        """
        self._check_incremental_settings()
        col_to_converters = self._get_col_to_converter(expected_features)

        pa_table = await self.source.async_execute_query(self, col_to_converters, connection)

        return self._postprocess_table(pa_table, expected_features)

    def _postprocess_table(self, pa_table: pa.Table, expected_features: Optional[Sequence[Feature]]):
        expected_feature_root_fqns = (
            None if expected_features is None else frozenset(x.root_fqn for x in expected_features)
        )
        col_name_mapping = self.get_col_name_mapping(tuple(pa_table.column_names), expected_feature_root_fqns)
        pa_table = pa_table.select(list(col_name_mapping.keys()))
        pa_table = pa_table.rename_columns([col_name_mapping[x] for x in pa_table.column_names])

        if self._finalizer == Finalizer.ONE:
            if len(pa_table) != 1:
                raise ValueError(f"Expected exactly one row; got {len(pa_table)} rows")

        if self._finalizer == Finalizer.ONE_OR_NONE:
            if len(pa_table) > 1:
                raise ValueError(f"Expected zero or one rows; got {len(pa_table)} rows")

        if self._finalizer in (Finalizer.ONE, Finalizer.ONE_OR_NONE, Finalizer.FIRST):
            pa_table = pa_table.slice(0, 1)
        return pa_table

    def execute_to_pyarrow_batches(
        self,
        expected_features: Optional[Sequence[Feature]] = None,
        connection: Optional[Connection] = None,
    ):
        if not hasattr(self.source, "execute_to_batches"):
            yield self.execute_to_pyarrow(expected_features, connection)

        if self.incremental_settings is not None:
            # FIXME: Move the incrementalization logic here, so then the `execute` and `execute_to_dataframe`
            # methods can take the hwm timestamp as a paramater, to allow for direct execution
            warnings.warn(
                (
                    "This query specified an incremental configuration, which has not been applied. "
                    "This is likely because the resolver is being executed directly. "
                    "The query will be attempted without any high-water-mark timestamp. "
                    "This will attempt to select all data, "
                    "or if the filters depend on the incremental timestamp, "
                    "will result in a query execution error. "
                )
            )
        expected_feature_root_fqns = (
            None if expected_features is None else frozenset(x.root_fqn for x in expected_features)
        )

        def converter_getters(column_names: List[str]) -> Dict[str, FeatureConverter]:
            # First map the column names to determine the feature fqns
            col_name_mapping = self.get_col_name_mapping(tuple(column_names), expected_feature_root_fqns)
            return {k: Feature.from_root_fqn(v).converter for (k, v) in col_name_mapping.items()}

        for pa_table in self.source.execute_to_batches(self, converter_getters, connection):
            col_name_mapping = self.get_col_name_mapping(tuple(pa_table.column_names), expected_feature_root_fqns)
            pa_table = pa_table.select(list(col_name_mapping.keys()))
            pa_table = pa_table.rename_columns([col_name_mapping[x] for x in pa_table.column_names])
            # if self._finalizer == Finalizer.ONE:
            #     if len(pa_table) != 1:
            #         raise ValueError(f"Expected exactly one row; got {len(pa_table)} rows")
            #
            # if self._finalizer == Finalizer.ONE_OR_NONE:
            #     if len(pa_table) > 1:
            #         raise ValueError(f"Expected zero or one rows; got {len(pa_table)} rows")
            #
            # if self._finalizer in (Finalizer.ONE, Finalizer.ONE_OR_NONE, Finalizer.FIRST):
            #     pa_table = pa_table.slice(0, 1)
            yield pa_table

    def execute_to_result_handles(
        self,
        expected_features: Optional[Sequence[Feature]] = None,
        connection: Optional[Connection] = None,
    ):
        if not hasattr(self.source, "execute_to_result_handles"):
            raise NotImplementedError

        if self.incremental_settings is not None:
            # FIXME: Move the incrementalization logic here, so then the `execute` and `execute_to_dataframe`
            # methods can take the hwm timestamp as a paramater, to allow for direct execution
            warnings.warn(
                (
                    "This query specified an incremental configuration, which has not been applied. "
                    "This is likely because the resolver is being executed directly. "
                    "The query will be attempted without any high-water-mark timestamp. "
                    "This will attempt to select all data, "
                    "or if the filters depend on the incremental timestamp, "
                    "will result in a query execution error. "
                )
            )
        expected_feature_root_fqns = (
            None if expected_features is None else frozenset(x.root_fqn for x in expected_features)
        )

        def converter_getters(column_names: List[str]) -> Dict[str, FeatureConverter]:
            # First map the column names to determine the feature fqns
            col_name_mapping = self.get_col_name_mapping(tuple(column_names), expected_feature_root_fqns)
            return {k: Feature.from_root_fqn(v).converter for (k, v) in col_name_mapping.items()}

        return self.source.execute_to_result_handles(self, converter_getters, connection)

    def execute_to_dataframe(
        self,
        expected_features: Optional[Sequence[Feature]] = None,
        connection: Optional[Connection] = None,
    ):
        """Actually execute the query, and return a DataFrame. Unlike :meth:`.execute`, this method will always keep the
        results as a DataFrame, even if the finalizer implies a singleton results (e.g. ONE, ONE_OR_NONE, or FIRST).

        Parameters
        ----------
        expected_features
            The list of expected features for the output, as provided by the resovler in which this query is executed.
            If not specified, the column names as returned by the query will be used to determine the output features.
        connection
            Execute the query using the supplied connection. If None (the default), then a new connection will be acquired
            from the underlying source for the query

        Returns
        -------
        DataFrame
            A `DataFrame`, even if the result contains 0 or 1 rows.
        """
        try:
            import polars as pl
        except ImportError:
            raise missing_dependency_exception("chalkpy[runtime]")
        pa_table = self.execute_to_pyarrow(expected_features, connection)
        df = pl.from_arrow(pa_table)
        assert isinstance(df, pl.DataFrame)
        return DataFrame(df)

    @functools.lru_cache(1024)
    def get_col_name_mapping(
        self,
        result_columns: Tuple[str, ...],
        expected_features: Optional[FrozenSet[str]],
    ):
        """Map the output columns to the expected feature names.

        Parameters
        ----------
        result_columns
            A list of the columns, in order, returned by the query.
        expected_features
            The expected feature root fqns for the query, as provided by the resolver signature.
            If a column name that is not in `fields` corresponds to a column in `expected_features`,
            then it will be mapped automatically.
            If a feature in `expected_features` does not have a corresponding output column,
            an error is raised.

        Returns
        -------
        dict[str, str]
            A mapping from output column names to root names.
        """
        ans: Dict[str, str] = {}
        normalized_to_original_col = {normalize_string_for_matching(x): x for x in result_columns}
        for k, v in self._fields.items():
            original_col_name = normalized_to_original_col.get(normalize_string_for_matching(k))
            if original_col_name is None:
                raise ValueError(f"Column {k} was not returned by the query.")
            ans[original_col_name] = v.root_fqn
        if expected_features is not None:
            unexpected_fields = [x for x in self._fields.values() if x.root_fqn not in expected_features]
            if len(unexpected_fields) > 0:
                raise ValueError(
                    f"Fields {unexpected_fields} were in the field mapping but are not included in the resolver output signature."
                )
            for normalized_col_name, original_col_name in normalized_to_original_col.items():
                if original_col_name not in ans:
                    maybe_matching_root_fqn = _get_matching_root_fqn(normalized_col_name, expected_features)
                    if maybe_matching_root_fqn is not None:
                        ans[original_col_name] = maybe_matching_root_fqn
        return ans
