from __future__ import annotations

import abc
import asyncio
import dataclasses
import functools
import inspect
from dataclasses import dataclass
from datetime import datetime
from inspect import Parameter, isclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Protocol,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

import pyarrow
from pydantic import BaseModel
from typing_extensions import ParamSpec, TypeAlias, get_args, get_origin

from chalk.features.dataframe import DataFrame, DataFrameMeta
from chalk.features.feature_field import Feature
from chalk.features.feature_set import Features, FeaturesMeta
from chalk.features.feature_wrapper import FeatureWrapper, unwrap_feature
from chalk.features.filter import Filter
from chalk.features.live_updates import register_live_updates_if_in_notebook
from chalk.features.tag import Environments, Tags
from chalk.sink import SinkIntegrationProtocol
from chalk.state import StateWrapper
from chalk.streams import StreamSource, get_name_with_duration
from chalk.streams.types import (
    StreamResolverParam,
    StreamResolverParamKeyedState,
    StreamResolverParamMessage,
    StreamResolverParamMessageWindow,
    StreamResolverSignature,
)
from chalk.utils import MachineType, notebook
from chalk.utils.annotation_parsing import ResolverAnnotationParser
from chalk.utils.cached_type_hints import cached_get_type_hints
from chalk.utils.collections import ensure_tuple
from chalk.utils.duration import CronTab, Duration, parse_chalk_duration
from chalk.utils.environment_parsing import env_var_bool
from chalk.utils.log_with_context import get_logger

try:
    from types import UnionType
except ImportError:
    UnionType = Union

if TYPE_CHECKING:
    from chalk.sql import BaseSQLSourceProtocol

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
P = ParamSpec("P")
V = TypeVar("V")

ResolverHook: TypeAlias = "Optional[Callable[[Resolver], None]]"

_logger = get_logger(__name__)


@dataclasses.dataclass(frozen=True)
class ResolverArgErrorHandler:
    default_value: Any


@dataclass
class StateDescriptor(Generic[T]):
    kwarg: str
    pos: int
    initial: T
    typ: Type[T]


class Cron:
    """
    Detailed options for specify the schedule and filtering
    functions for Chalk batch jobs.
    """

    def __init__(
        self,
        schedule: Union[CronTab, Duration],
        filter: Optional[Callable[..., bool]] = None,
        sample: Optional[Callable[[], DataFrame]] = None,
    ):
        """Run an online or offline resolver on a schedule.

        This class lets you add a filter or sample function
        to your cron schedule for a resolver. See the
        overloaded signatures for more information.

        Parameters
        ----------
        schedule
            The period of the cron job. Can be either a crontab (`"0 * * * *"`)
            or a `Duration` (`"2h"`).
        filter
            Optionally, a function to filter down the arguments to consider.

            See https://docs.chalk.ai/docs/resolver-cron#filtering-examples for more information.
        sample
            Explicitly provide the sample function for the cron job.

            See https://docs.chalk.ai/docs/resolver-cron#custom-examples for more information.


        Examples
        --------
        Using a filter

        >>> def fltr(v: Account.active):
        ...     return v
        >>> @online(cron=Cron(schedule="1d", filter=fltr))
        ... def fn(balance: Account.balance) -> ...:

        Using a sample function

        >>> def s() -> DataFrame[User.id]:
        ...     return DataFrame.read_csv(...)
        >>> @offline(cron=Cron(schedule="1d", sample=s))
        ... def fn(balance: User.account.balance) -> ...:
        """
        self.schedule = schedule
        self.filter = filter
        self.sample = sample
        self.trigger_downstream = False


def _flatten_features(output: Optional[Type[Features]]) -> Sequence[Feature]:
    if output is None:
        return []
    features = output.features
    if len(features) == 1 and isinstance(features[0], type) and issubclass(features[0], DataFrame):
        return features[0].columns
    return features


class ResolverProtocol(Protocol[P, T_co]):
    """A resolver, returned from the decorators `@offline` and `@online`."""

    fqn: str
    """The name of the resolver, either given by the name of the function,
    or by the keyword argument `name` given to `@offline` or `@online`.
    """

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T_co:
        """Returns the result of calling the function decorated
        with `@offline` or `@online` with the given arguments.

        Parameters
        ----------
        args
            The arguments to pass to the decorated function.

        Returns
        -------
        T
            The result of calling the decorated function
            with `args`
            Useful for unit-testing.

            Read more at https://docs.chalk.ai/docs/unit-tests

        Examples
        --------
        >>> from chalk.features import online
        >>> @online
        ... def fn(a: int, b: int) -> int:
        ...     return a + b
        >>> assert fn(1, 2) == 3
        """
        ...


class Resolver(ResolverProtocol[P, T], abc.ABC):
    function_definition: str
    fqn: str
    filename: str
    inputs: List[Feature]
    output: Optional[Type[Features]]
    fn: Callable[P, T]
    environment: Optional[List[str]]
    tags: Optional[List[str]]
    max_staleness: Optional[Duration]
    machine_type: Optional[MachineType]
    owner: Optional[str]
    state: Optional[StateDescriptor]
    default_args: List[Optional[ResolverArgErrorHandler]]

    # TODO make this a map by fqn like we do for Features
    registry: "ClassVar[List[Resolver]]" = []

    hook: ResolverHook = None

    def __eq__(self, other: object):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.fqn == other.fqn

    def __hash__(self):
        return hash(self.fqn)

    @property
    def __name__(self):
        return self.fn.__name__

    def _process_call(self, *args: P.args, **kwargs: P.kwargs) -> T:
        # __call__ is defined to support userland code that invokes a resolver
        # as if it is a normal python function
        # If the user returns a ChalkQuery, then we'll want to automatically execute it
        from chalk.sql import FinalizedChalkQuery
        from chalk.sql._internal.chalk_query import ChalkQuery
        from chalk.sql._internal.string_chalk_query import StringChalkQuery

        result = self.fn(*args, **kwargs)

        if isinstance(result, (ChalkQuery, StringChalkQuery)):
            result = result.all()
        if isinstance(result, FinalizedChalkQuery):
            result = result.execute(_flatten_features(self.output))
        return result

    async def _process_async_call(self, *args: P.args, **kwargs: P.kwargs):
        # __call__ is defined to support userland code that invokes a resolver
        # as if it is a normal python function
        # If the user returns a ChalkQuery, then we'll want to automatically execute it
        from chalk.sql import FinalizedChalkQuery
        from chalk.sql._internal.chalk_query import ChalkQuery
        from chalk.sql._internal.string_chalk_query import StringChalkQuery

        assert asyncio.iscoroutinefunction(self.fn)

        result = await self.fn(*args, **kwargs)

        if isinstance(result, (ChalkQuery, StringChalkQuery)):
            result = result.all()
        if isinstance(result, FinalizedChalkQuery):
            result = await result.async_execute(_flatten_features(self.output))
        return result

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if asyncio.iscoroutinefunction(self.fn):
            # Not awaiting this coroutine here -- when the caller awaits it,
            # it will run
            return cast(T, self._process_async_call(*args, **kwargs))
        else:
            return self._process_call(*args, **kwargs)

    @classmethod
    def add_to_registry(cls, r: Resolver):
        """
        Adds the given resolver to the registry.
        If in a notebook, first removes any existing resolvers with the same FQN.
        """
        if notebook.is_notebook():
            new_resolvers = [r2 for r2 in cls.registry if r2.name != r.name]
            new_resolvers.append(r)
            cls.registry[:] = new_resolvers
        else:
            cls.registry.append(r)

    @functools.cached_property
    def name(self) -> str:
        return self.fqn.split(".")[-1]


register_live_updates_if_in_notebook(Resolver)


class SinkResolver(Resolver[P, T]):
    registry: "List[SinkResolver]" = []

    def __init__(
        self,
        function_definition: str,
        fqn: str,
        filename: str,
        doc: Optional[str],
        inputs: List[Feature],
        fn: Callable[P, T],
        environment: Optional[List[str]],
        tags: Optional[List[str]],
        machine_type: Optional[MachineType],
        buffer_size: Optional[int],
        debounce: Optional[Duration],
        max_delay: Optional[Duration],
        upsert: Optional[bool],
        owner: Optional[str],
        input_is_df: bool,
        default_args: List[Optional[ResolverArgErrorHandler]],
        integration: Optional[Union[BaseSQLSourceProtocol, SinkIntegrationProtocol]] = None,
    ):
        self.owner = owner
        self.function_definition = function_definition
        self.fqn = fqn
        self.filename = filename
        self.inputs = inputs
        self.fn = fn
        self.__module__ = fn.__module__
        self.__doc__ = fn.__doc__
        self.__annotations__ = fn.__annotations__
        self.environment = environment
        self.tags = tags
        self.doc = doc
        self.machine_type = machine_type
        self.buffer_size = buffer_size
        if isinstance(debounce, str):
            debounce = parse_chalk_duration(debounce)
        self.debounce = debounce
        if isinstance(max_delay, str):
            max_delay = parse_chalk_duration(max_delay)
        self.max_delay = max_delay
        self.upsert = upsert
        self.integration = integration
        self.default_args = default_args
        self.max_staleness = None
        self.state = None
        self.output = None
        self.input_is_df = input_is_df

    def __repr__(self):
        return f"SinkResolver(name={self.fqn})"


class OnlineResolver(Resolver[P, T]):
    def __init__(
        self,
        function_definition: str,
        fqn: str,
        filename: str,
        doc: Optional[str],
        inputs: List[Feature],
        output: Type[Features],
        fn: Callable[P, T],
        environment: Optional[List[str]],
        tags: Optional[List[str]],
        max_staleness: Optional[Duration],
        cron: Optional[Union[CronTab, Duration, Cron]],
        machine_type: Optional[MachineType],
        when: Optional[Filter],
        state: Optional[StateDescriptor],
        default_args: List[Optional[ResolverArgErrorHandler]],
        owner: Optional[str],
        timeout: Optional[Duration],
        is_sql_file_resolver: bool = False,
    ):
        self.function_definition = function_definition
        self.fqn = fqn
        self.filename = filename
        self.inputs = inputs
        self.output = output
        self.fn = fn
        self.__module__ = fn.__module__
        self.__doc__ = fn.__doc__
        self.__annotations__ = fn.__annotations__
        self.environment = environment
        self.tags = tags
        self.max_staleness = max_staleness
        self.cron = cron
        self.doc = doc
        self.machine_type = machine_type
        self.when = when
        self.state = state
        self.default_args = default_args
        self.owner = owner
        if isinstance(timeout, str):
            timeout = parse_chalk_duration(timeout)
        self.timeout = timeout
        self.is_sql_file_resolver = is_sql_file_resolver

    def __repr__(self):
        return f"OnlineResolver(name={self.fqn})"


class OfflineResolver(Resolver[P, T]):
    def __init__(
        self,
        function_definition: str,
        fqn: str,
        filename: str,
        doc: Optional[str],
        inputs: List[Feature],
        output: Type[Features],
        fn: Callable[P, T],
        environment: Optional[List[str]],
        tags: Optional[List[str]],
        max_staleness: Optional[Duration],
        cron: Optional[Union[CronTab, Duration, Cron]],
        machine_type: Optional[MachineType],
        state: Optional[StateDescriptor],
        when: Optional[Filter],
        default_args: List[Optional[ResolverArgErrorHandler]],
        owner: Optional[str],
        timeout: Optional[Duration],
        is_sql_file_resolver: bool = False,
    ):
        self.when = when
        self.function_definition = function_definition
        self.fqn = fqn
        self.filename = filename
        self.doc = doc
        self.inputs = inputs
        self.output = output
        self.fn = fn
        self.__module__ = fn.__module__
        self.__doc__ = fn.__doc__
        self.__annotations__ = fn.__annotations__
        self.environment = environment
        self.tags = tags
        self.max_staleness = max_staleness
        self.cron = cron
        self.machine_type = machine_type
        self.state = state
        self.default_args = default_args
        self.owner = owner
        if isinstance(timeout, str):
            timeout = parse_chalk_duration(timeout)
        self.timeout = timeout
        self.is_sql_file_resolver = is_sql_file_resolver

    def __repr__(self):
        return f"OfflineResolver(name={self.fqn})"


@dataclasses.dataclass(frozen=True)
class ResolverParseResult(Generic[P, T]):
    fqn: str
    inputs: List[Feature]
    state: Optional[StateDescriptor]
    output: Optional[Type[Features]]
    function: Callable[P, T]
    function_definition: str
    doc: Optional[str]
    default_args: List[Optional[ResolverArgErrorHandler]]


@dataclasses.dataclass(frozen=True)
class SinkResolverParseResult(Generic[P, T]):
    fqn: str
    input_features: List[Feature]
    input_is_df: bool
    function: Callable[P, T]
    function_definition: str
    doc: Optional[str]
    input_feature_defaults: List[Optional[ResolverArgErrorHandler]]


def get_resolver_fqn(function: Callable):
    return f"{function.__module__}.{function.__name__}"


def get_state_default_value(
    state_typ: type,
    declared_default: Any,
    parameter_name_for_errors: str,
    resolver_fqn_for_errors: str,
) -> Any:
    if not issubclass(state_typ, BaseModel) and not dataclasses.is_dataclass(state_typ):
        raise ValueError(
            (
                f"State value must be a pydantic model or dataclass, "
                f"but argument '{parameter_name_for_errors}' has type '{type(state_typ).__name__}'"
            )
        )

    default = declared_default
    if default is inspect.Signature.empty:
        try:
            default = state_typ()
        except Exception as e:
            cls_name = state_typ.__name__
            raise ValueError(
                (
                    "State parameter must have a default value, or be able to be instantiated "
                    f"with no arguments. For resolver '{resolver_fqn_for_errors}', no default found, and default "
                    f"construction failed with '{str(e)}'. Assign a default in the resolver's "
                    f"signature ({parameter_name_for_errors}: {cls_name} = {cls_name}(...)), or assign a default"
                    f" to each of the fields of '{cls_name}'."
                )
            )

    if not isinstance(default, state_typ):
        raise ValueError(
            f"Expected type '{state_typ.__name__}' for '{parameter_name_for_errors}', but default has type '{type(default).__name__}'"
        )

    return default


def _explode_windowed_features(ret_val: Type[Features]) -> Type[Features]:
    new_features = []
    has_windowed = False
    is_dataframe = False

    if (
        len(ret_val.features) == 1
        and isinstance(ret_val.features[0], type)
        and issubclass(ret_val.features[0], DataFrame)
    ):
        is_dataframe = True

    for f in _flatten_features(ret_val):
        if isinstance(f, Feature) and f.is_windowed:
            has_windowed = True
            for d in f.window_durations:
                windowed_name = get_name_with_duration(name_or_fqn=f.name, duration=d)
                windowed_feature = getattr(f.features_cls, windowed_name)
                new_features.append(unwrap_feature(windowed_feature))
        else:
            new_features.append(f)

    if not has_windowed:
        return ret_val

    return Features[DataFrame[new_features]] if is_dataframe else Features[new_features]


def parse_function(
    fn: Callable[P, T],
    glbs: Optional[Dict[str, Any]],
    lcls: Optional[Dict[str, Any]],
    ignore_return: bool = False,
    allow_custom_args: bool = False,
    is_streaming_resolver: bool = False,
) -> ResolverParseResult[P, T]:
    fqn = get_resolver_fqn(function=fn)
    sig = inspect.signature(fn)
    annotation_parser = ResolverAnnotationParser(fn, glbs, lcls)

    function_definition = inspect.getsource(fn)
    return_annotation = cached_get_type_hints(fn).get("return")
    if return_annotation is None and not ignore_return:
        raise TypeError(
            f"Resolver '{fqn}' must have a return annotation. See https://docs.chalk.ai/docs/resolver-outputs for more information."
        )

    ret_val = None

    if isinstance(return_annotation, FeatureWrapper):
        return_annotation = return_annotation._chalk_feature

    if isinstance(return_annotation, Feature):
        assert return_annotation.typ is not None

        if return_annotation.is_has_many:
            assert issubclass(return_annotation.typ.parsed_annotation, DataFrame)
            ret_val = Features[return_annotation.typ.parsed_annotation.columns]
        elif return_annotation.is_has_one:
            assert return_annotation.joined_class is not None
            ret_val = Features[return_annotation.joined_class.features]
        else:
            # function annotated like def get_account_id(user_id: User.id) -> User.account_id
            ret_val = Features[return_annotation]

    if ret_val is None and not ignore_return:
        if not isinstance(return_annotation, type):
            raise TypeError(f"return_annotation {return_annotation} of type {type(return_annotation)} is not a type")
        if issubclass(return_annotation, Features):
            # function annotated like def get_account_id(user_id: User.id) -> Features[User.account_id]
            # or def get_account_id(user_id: User.id) -> User:
            ret_val = return_annotation
        elif issubclass(return_annotation, DataFrame):
            # function annotated like def get_transactions(account_id: Account.id) -> DataFrame[Transaction]
            ret_val = Features[return_annotation]

    if ret_val is None and not ignore_return:
        raise ValueError(f"Resolver {fqn} did not have a valid return type")

    if not is_streaming_resolver:
        ret_val = _explode_windowed_features(ret_val)

    inputs = [annotation_parser.parse_annotation(p) for p in sig.parameters.keys()]

    # Unwrap anything that is wrapped with FeatureWrapper
    inputs = [unwrap_feature(p) if isinstance(p, FeatureWrapper) else p for p in inputs]

    if len(inputs) == 0:
        default_arg_count = 0
    elif isinstance(inputs[0], DataFrameMeta):
        default_arg_count = len(inputs[0].columns)
    else:
        default_arg_count = len(inputs)

    state = None
    default_args: List[Optional[ResolverArgErrorHandler]] = [None for _ in range(default_arg_count)]

    for i, (arg_name, parameter) in enumerate(sig.parameters.items()):
        bad_input = lambda: ValueError(
            (
                f"Resolver inputs must be Features, DataFrame, or State. "
                f"Received {str(inputs[i])} for argument '{arg_name}' for '{fqn}'."
            )
        )
        arg = inputs[i]

        if get_origin(arg) in (UnionType, Union):
            args = get_args(arg)
            if len(args) != 2:
                raise bad_input()
            if type(None) not in args:
                raise bad_input()
            real_arg = next((a for a in args if a is not type(None)), None)
            if real_arg is None:
                raise bad_input()
            default_args[i] = ResolverArgErrorHandler(None)
            arg = unwrap_feature(real_arg)
            inputs[i] = arg

        if parameter.empty != parameter.default:
            default_args[i] = ResolverArgErrorHandler(parameter.default)

        if not isinstance(arg, (StateWrapper, Feature, DataFrameMeta)):
            if allow_custom_args:
                continue
            raise bad_input()

        if isinstance(arg, Feature) and (arg.is_windowed or arg.typ.is_windowed):
            # Windowed arguments in resolver signatures must specify a window bucket
            available_windows = ", ".join(f"{x}s" for x in arg.window_durations)
            raise ValueError(
                (
                    f"Resolver argument '{arg_name}' to '{fqn}' does not select a window. "
                    f"Add a selected window, like {arg.name}('{next(iter(arg.window_durations), '')}'). "
                    f"Available windows: {available_windows}."
                )
            )

        if not isinstance(arg, StateWrapper):
            continue

        if state is not None:
            raise ValueError(
                f"Only one state argument is allowed. Two provided to '{fqn}': '{state.kwarg}' and '{arg_name}'"
            )

        arg_name = parameter.name

        state = StateDescriptor(
            kwarg=arg_name,
            pos=i,
            initial=get_state_default_value(
                state_typ=arg.typ,
                resolver_fqn_for_errors=fqn,
                parameter_name_for_errors=arg_name,
                declared_default=parameter.default,
            ),
            typ=arg.typ,
        )

    assert ret_val is None or issubclass(ret_val, Features)
    if not ignore_return and ret_val is not None and issubclass(ret_val, Features):
        # Streaming resolvers are themselves windowed, so the outputs must not specify a window explicitly.
        for f in _flatten_features(ret_val):
            if f.is_windowed_pseudofeature and is_streaming_resolver:
                feature_name_without_duration = "__".join(f.root_fqn.split("__")[:-1])  # A bit hacky, but should work
                raise TypeError(
                    (
                        "Streaming resolvers should not resolve features of a particular window period in the return type"
                        f"Resolver '{fn.__name__}' returned feature '{f.root_fqn}'. Instead, return {feature_name_without_duration}"
                    )
                )
    state_index = state.pos if state is not None else None
    return ResolverParseResult(
        fqn=fqn,
        inputs=[v for i, v in enumerate(inputs) if i != state_index],
        output=ret_val,
        function=fn,
        function_definition=function_definition,
        doc=fn.__doc__,
        state=state,
        default_args=default_args,
    )


def parse_sink_function(
    fn: Callable[P, T],
    glbs: Optional[Dict[str, Any]],
    lcls: Optional[Dict[str, Any]],
) -> SinkResolverParseResult[P, T]:
    fqn = get_resolver_fqn(function=fn)
    sig = inspect.signature(fn)
    annotation_parser = ResolverAnnotationParser(fn, glbs, lcls)
    function_definition = inspect.getsource(fn)
    annotations = [annotation_parser.parse_annotation(p) for p in sig.parameters.keys()]

    if len(annotations) == 1 and isinstance(annotations[0], DataFrameMeta):
        # It looks like the user's function wants a DataFrame of features
        df = annotations[0]
        features = df.columns

        return SinkResolverParseResult(
            fqn=fqn,
            input_is_df=True,
            function=fn,
            function_definition=function_definition,
            doc=fn.__doc__,
            input_feature_defaults=[None for _ in range(len(features))],
            input_features=list(features),
        )

    else:
        # It looks like the user's function wants features as individual parameters
        feature_default_values: List[Optional[ResolverArgErrorHandler]] = []
        feature_inputs = []

        for i, (arg_name, parameter) in enumerate(sig.parameters.items()):
            arg = annotations[i]
            default_value = None
            if isinstance(arg, FeatureWrapper):
                # Unwrap anything that is wrapped with FeatureWrapper
                arg = unwrap_feature(arg)

            bad_input = lambda: ValueError(
                f"Sink resolver inputs must be Features. Received {str(arg)} for argument '{arg_name}' for '{fqn}'.\n"
            )

            if get_origin(arg) in (UnionType, Union):  # Optional[] handling
                args = get_args(arg)
                if len(args) != 2:
                    raise bad_input()
                if type(None) not in args:
                    raise bad_input()
                real_arg = next((a for a in args if a is not type(None)), None)
                if real_arg is None:
                    raise bad_input()
                default_value = ResolverArgErrorHandler(None)
                arg = unwrap_feature(real_arg)

            if not isinstance(arg, Feature):
                raise bad_input()

            if parameter.empty != parameter.default:
                default_value = ResolverArgErrorHandler(parameter.default)

            feature_default_values.append(default_value)
            feature_inputs.append(arg)

        return SinkResolverParseResult(
            fqn=fqn,
            input_features=feature_inputs,
            function=fn,
            function_definition=function_definition,
            doc=fn.__doc__,
            input_is_df=False,
            input_feature_defaults=feature_default_values,
        )


@overload
def online(
    *,
    environment: Optional[Environments] = None,
    tags: Optional[Tags] = None,
    cron: Optional[Union[CronTab, Duration, Cron]] = None,
    machine_type: Optional[MachineType] = None,
    when: Optional[Any] = None,
    owner: Optional[str] = None,
    timeout: Optional[Duration] = None,
) -> Callable[[Callable[P, T]], ResolverProtocol[P, T]]:
    ...


@overload
def online(
    fn: Callable[P, T],
    /,
) -> ResolverProtocol[P, T]:
    ...


def online(
    fn: Optional[Callable[P, T]] = None,
    /,
    *,
    environment: Optional[Environments] = None,
    tags: Optional[Tags] = None,
    cron: Optional[Union[CronTab, Duration, Cron]] = None,
    machine_type: Optional[MachineType] = None,
    when: Optional[Any] = None,
    owner: Optional[str] = None,
    timeout: Optional[Duration] = None,
) -> Union[Callable[[Callable[P, T]], ResolverProtocol[P, T]], ResolverProtocol[P, T]]:
    """Decorator to create an online resolver.

    Parameters
    ----------
    environment
        Environments are used to trigger behavior
        in different deployments such as staging, production, and
        local development. For example, you may wish to interact with
        a vendor via an API call in the production environment, and
        opt to return a constant value in a staging environment.

        Environment can take one of three types:
            - `None` (default) - candidate to run in every environment
            - `str` - run only in this environment
            - `list[str]` - run in any of the specified environment and no others

        Read more at https://docs.chalk.ai/docs/resolver-environments
    owner
        Individual or team responsible for this resolver.
        The Chalk Dashboard will display this field, and alerts
        can be routed to owners.
    tags
        Allow you to scope requests within an
        environment. Both tags and environment need to match for a
        resolver to be a candidate to execute.

        You might consider using tags, for example, to change out
        whether you want to use a sandbox environment for a vendor,
        or to bypass the vendor and return constant values in a
        staging environment.

        Read more at https://docs.chalk.ai/docs/resolver-tags
    cron
        You can schedule resolvers to run on a pre-determined
        schedule via the cron argument to resolver decorators.

        Cron can sample all examples, a subset of all examples,
        or a custom provided set of examples.

        Read more at https://docs.chalk.ai/docs/resolver-cron
    timeout
        You can specify the maximum duration to wait for the
        resolver's result. Once the resolver's runtime exceeds
        the specified duration, a timeout error will be returned
        along with each output feature.

        Please use supported Chalk durations
        'w', 'd', 'h', 'm', 's', and/or 'ms'.

        Read more at https://docs.chalk.ai/docs/timeout
                 and https://docs.chalk.ai/docs/duration
    when
        Like tags, `when` can filter when a resolver is eligible
        to run. Unlike tags, `when` can use feature values,
        so that you can write resolvers like:

        >>> @batch(when=User.risk_profile == "low" or User.is_employee)
        ... def resolver_fn(...) -> ...:
        ...     ...

    Other Parameters
    ----------------
    fn
        The function that you're decorating as a resolver.
    machine_type
        You can optionally specify that resolvers need to run on a
        machine other than the default. Must be configured in your
        deployment.

    Returns
    -------
    Union[Callable[[Callable[P, T]], ResolverProtocol[P, T]], ResolverProtocol[P, T]]
        A `ResolverProtocol` which can be called as a normal function! You can unit-test
        resolvers as you would unit-test any other code.

        Read more at https://docs.chalk.ai/docs/unit-tests

    Examples
    --------
    >>> @online
    ... def name_match(
    ...     name: User.full_name,
    ...     account_name: User.bank_account.title
    ... ) -> User.account_name_match_score:
    ...     if name.lower() == account_name.lower():
    ...         return 1.
    ...     return 0.
    """
    frame = inspect.currentframe()
    assert frame is not None
    caller_frame = frame.f_back
    assert caller_frame is not None
    caller_globals = caller_frame.f_globals
    caller_locals = caller_frame.f_locals

    def decorator(fn: Callable[P, T]):
        caller_filename = inspect.getsourcefile(fn) or "<unknown file>"
        parsed = parse_function(fn, caller_globals, caller_locals)
        if (
            not env_var_bool("CHALK_ALLOW_REGISTRY_UPDATES")
            and parsed.fqn in {s.fqn for s in Resolver.registry}
            and not notebook.is_notebook()
        ):
            raise ValueError(f"Duplicate resolver {parsed.fqn}")
        if parsed.output is None:
            raise ValueError(f"Online resolvers must return features; '{parsed.fqn}' returns None")

        resolver = OnlineResolver(
            filename=caller_filename,
            function_definition=parsed.function_definition,
            fqn=parsed.fqn,
            doc=parsed.doc,
            inputs=parsed.inputs,
            output=parsed.output,
            fn=fn,
            environment=None if environment is None else list(ensure_tuple(environment)),
            tags=None if tags is None else list(ensure_tuple(tags)),
            max_staleness=None,
            cron=cron,
            machine_type=machine_type,
            when=when,
            owner=owner,
            state=parsed.state,
            default_args=parsed.default_args,
            timeout=timeout,
        )

        Resolver.add_to_registry(resolver)
        if Resolver.hook:
            Resolver.hook(resolver)

        # Return the decorated resolver, which notably implements __call__() so it acts the same as
        # the underlying function if called directly, e.g. from test code
        return resolver

    return decorator(fn) if fn else decorator


@overload
def offline(
    *,
    environment: Optional[Environments] = None,
    tags: Optional[Tags] = None,
    cron: Optional[Union[CronTab, Duration, Cron]] = None,
    machine_type: Optional[MachineType] = None,
    when: Optional[Any] = None,
    owner: Optional[str] = None,
) -> Callable[[Callable[P, T]], ResolverProtocol[P, T]]:
    ...


@overload
def offline(
    fn: Callable[P, T],
    /,
) -> ResolverProtocol[P, T]:
    ...


def offline(
    fn: Optional[Callable[P, T]] = None,
    /,
    *,
    environment: Optional[Environments] = None,
    tags: Optional[Tags] = None,
    cron: Optional[Union[CronTab, Duration, Cron]] = None,
    machine_type: Optional[MachineType] = None,
    when: Optional[Any] = None,
    owner: Optional[str] = None,
    timeout: Optional[Duration] = None,
) -> Union[Callable[[Callable[P, T]], Callable[P, T]], ResolverProtocol[P, T]]:
    """Decorator to create an offline resolver.

    Parameters
    ----------
    environment
        Environments are used to trigger behavior
        in different deployments such as staging, production, and
        local development. For example, you may wish to interact with
        a vendor via an API call in the production environment, and
        opt to return a constant value in a staging environment.

        Environment can take one of three types:
            - `None` (default) - candidate to run in every environment
            - `str` - run only in this environment
            - `list[str]` - run in any of the specified environment and no others

        Read more at https://docs.chalk.ai/docs/resolver-environments
    owner
        Allows you to specify an individual or team
        who is responsible for this resolver. The Chalk Dashboard
        will display this field, and alerts can be routed to owners.
    tags
        Allow you to scope requests within an
        environment. Both tags and environment need to match for a
        resolver to be a candidate to execute.

        You might consider using tags, for example, to change out
        whether you want to use a sandbox environment for a vendor,
        or to bypass the vendor and return constant values in a
        staging environment.

        Read more at https://docs.chalk.ai/docs/resolver-tags
    cron
        You can schedule resolvers to run on a pre-determined
        schedule via the cron argument to resolver decorators.

        Cron can sample all examples, a subset of all examples,
        or a custom provided set of examples.

        Read more at https://docs.chalk.ai/docs/resolver-cron
    timeout
        You can specify the maximum duration to wait for the
        resolver's result. Once the resolver's runtime exceeds
        the specified duration, a timeout error will be raised.

        Please use supported Chalk durations
        'w', 'd', 'h', 'm', 's', and/or 'ms'.

        Read more at https://docs.chalk.ai/docs/timeout
                 and https://docs.chalk.ai/docs/duration
    when
        Like tags, `when` can filter when a resolver
        is eligible to run. Unlike tags, `when` can use feature values,
        so that you can write resolvers like::

        >>> @offline(when=User.risk_profile == "low" or User.is_employee)
        ... def resolver_fn(...) -> ...:
        ...    ...

    Other Parameters
    ----------------
    fn
        The function that you're decorating as a resolver.
    machine_type
        You can optionally specify that resolvers need to run on
        a machine other than the default. Must be configured in
        your deployment.

    Returns
    -------
    Union[Callable[[Callable[P, T]], ResolverProtocol[P, T]], ResolverProtocol[P, T]]
        A `ResolverProtocol` which can be called as a normal function! You can unit-test
        resolvers as you would unit-test any other code.

        Read more at https://docs.chalk.ai/docs/unit-tests

    Examples
    --------
    >>> @offline(cron="1h")
    ... def get_fraud_score(
    ...     email: User.email,
    ...     name: User.name,
    ... ) -> User.fraud_score:
    ...     return socure.get_sigma_score(email, name)
    """
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename
    caller_globals = caller_frame.frame.f_globals
    caller_locals = caller_frame.frame.f_locals

    def decorator(fn: Callable[P, T]):
        parsed = parse_function(fn, caller_globals, caller_locals)
        if (
            not env_var_bool("CHALK_ALLOW_REGISTRY_UPDATES")
            and parsed.fqn in {s.fqn for s in Resolver.registry}
            and not notebook.is_notebook()
        ):
            raise ValueError(f"Duplicate resolver {parsed.fqn}")
        if parsed.output is None:
            raise ValueError(f"Offline resolvers must return features; '{parsed.fqn}' returns None")
        resolver = OfflineResolver(
            filename=caller_filename,
            function_definition=parsed.function_definition,
            fqn=parsed.fqn,
            doc=parsed.doc,
            inputs=parsed.inputs,
            output=parsed.output,
            fn=fn,
            environment=None if environment is None else list(ensure_tuple(environment)),
            tags=None if tags is None else list(ensure_tuple(tags)),
            max_staleness=None,
            cron=cron,
            machine_type=machine_type,
            state=parsed.state,
            when=when,
            owner=owner,
            default_args=parsed.default_args,
            timeout=timeout,
        )
        Resolver.add_to_registry(resolver)
        if Resolver.hook:
            Resolver.hook(resolver)
        return resolver

    return decorator(fn) if fn else decorator


@overload
def sink(
    *,
    environment: Optional[Environments] = None,
    tags: Optional[Tags] = None,
    machine_type: Optional[MachineType] = None,
    buffer_size: Optional[int] = None,
    debounce: Optional[Duration] = None,
    max_delay: Optional[Duration] = None,
    upsert: Optional[bool] = None,
    integration: Optional[Union[BaseSQLSourceProtocol, SinkIntegrationProtocol]] = None,
    owner: Optional[str] = None,
) -> Callable[[Callable[P, T]], ResolverProtocol[P, T]]:
    ...


@overload
def sink(
    fn: Callable[P, T],
    /,
) -> ResolverProtocol[P, T]:
    ...


def sink(
    fn: Optional[Callable[P, T]] = None,
    /,
    *,
    environment: Optional[Environments] = None,
    tags: Optional[Tags] = None,
    machine_type: Optional[MachineType] = None,
    buffer_size: Optional[int] = None,
    debounce: Optional[Duration] = None,
    max_delay: Optional[Duration] = None,
    upsert: Optional[bool] = None,
    integration: Optional[Union[BaseSQLSourceProtocol, SinkIntegrationProtocol]] = None,
    owner: Optional[str] = None,
) -> Union[Callable[[Callable[P, T]], ResolverProtocol[P, T]], ResolverProtocol[P, T]]:
    """Decorator to create a sink.
    Read more at https://docs.chalk.ai/docs/sinks

    Parameters
    ----------
    environment
        Environments are used to trigger behavior
        in different deployments such as staging, production, and
        local development. For example, you may wish to interact with
        a vendor via an API call in the production environment, and
        opt to return a constant value in a staging environment.

        Environment can take one of three types:
            - `None` (default) - candidate to run in every environment
            - `str` - run only in this environment
            - `list[str]` - run in any of the specified environment and no others

        Read more at https://docs.chalk.ai/docs/resolver-environments
    tags
        Allow you to scope requests within an
        environment. Both tags and environment need to match for a
        resolver to be a candidate to execute.

        You might consider using tags, for example, to change out
        whether you want to use a sandbox environment for a vendor,
        or to bypass the vendor and return constant values in a
        staging environment.

        Read more at https://docs.chalk.ai/docs/resolver-tags
    buffer_size
        Count of updates to buffer.
    owner
        The individual or team responsible for this resolver.
        The Chalk Dashboard will display this field, and alerts
        can be routed to owners.

    Other Parameters
    ----------------
    fn
        The function that you're decorating as a resolver.
    machine_type
        You can optionally specify that resolvers need to run on a
        machine other than the default. Must be configured in your
        deployment.
    debounce
    max_delay
    upsert
    integration

    Examples
    --------
    >>> @sink
    ... def process_updates(
    ...     uid: User.id,
    ...     email: User.email,
    ...     phone: User.phone,
    ... ):
    ...     user_service.update(
    ...         uid=uid,
    ...         email=email,
    ...         phone=phone
    ...     )
    >>> process_updates(123, "sam@chalk.ai", "555-555-5555")

    Returns
    -------
    Callable[[Any, ...], Any]
        A callable function! You can unit-test sinks as you
        would unit test any other code.
        Read more at https://docs.chalk.ai/docs/unit-tests
    """
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename
    caller_globals = caller_frame.frame.f_globals
    caller_locals = caller_frame.frame.f_locals

    def decorator(fn: Callable[P, T]):
        parsed = parse_sink_function(fn, caller_globals, caller_locals)
        resolver = SinkResolver(
            filename=caller_filename,
            function_definition=parsed.function_definition,
            fqn=parsed.fqn,
            doc=parsed.doc,
            inputs=parsed.input_features,
            fn=fn,
            environment=None if environment is None else list(ensure_tuple(environment)),
            tags=None if tags is None else list(ensure_tuple(tags)),
            machine_type=machine_type,
            buffer_size=buffer_size,
            debounce=debounce,
            max_delay=max_delay,
            upsert=upsert,
            integration=integration,
            owner=owner,
            default_args=parsed.input_feature_defaults,
            input_is_df=parsed.input_is_df,
        )
        SinkResolver.registry.append(resolver)
        return resolver

    return decorator(fn) if fn else decorator


class StreamResolver(Resolver[P, T]):
    registry: "List[StreamResolver]" = []
    mode: Optional[Literal["continuous", "tumbling"]]

    def __init__(
        self,
        function_definition: str,
        fqn: str,
        filename: str,
        source: StreamSource,
        fn: Callable[P, T],
        environment: Optional[List[str]],
        doc: Optional[str],
        mode: Optional[Literal["continuous", "tumbling"]],
        module: str,
        machine_type: Optional[str],
        message: Optional[Type[Any]],
        output: Type[Features],
        signature: StreamResolverSignature,
        state: Optional[StateDescriptor],
        sql_query: Optional[str],
        owner: Optional[str],
        parse: Optional[ParseInfo],
        keys: Optional[dict[str, Any]],
        timestamp: Optional[str],
    ):
        self.function_definition = function_definition
        self.fqn = fqn
        self.filename = filename
        self.inputs = []
        self.doc = doc
        self.source = source
        self.fn = fn
        self.environment = environment
        self.__doc__ = doc
        self.__module__ = module
        self.machine_type = machine_type
        self.max_staleness = None
        self.message = message
        self.output = output
        self.mode = mode
        self.signature = signature
        self.state = state
        self.sql_query = sql_query
        self.tags = None
        self.default_args = []
        self.owner = owner
        self.parse = parse
        self.keys = keys
        self.timestamp = timestamp
        fqn_to_windows = {o.fqn: o.window_durations for o in _flatten_features(self.output) if o.is_windowed}
        if len(set(tuple(v) for v in fqn_to_windows.values())) > 1:
            fqn_to_declared_windows = {
                o.fqn: sorted(o.window_durations) for o in _flatten_features(self.output) if o.is_windowed
            }
            periods = [f'{fqn}[{", ".join(f"{window}s")}]' for fqn, window in fqn_to_declared_windows.items()]
            raise ValueError((f"All features must have the same window periods. Found " f"{', '.join(periods)}"))
        self.window_periods_seconds = next(iter(fqn_to_windows.values()), ())
        # Mapping of window (in secs) to mapping of (original feature, windowed pseudofeature)
        self.windowed_pseudofeatures: Dict[int, Dict[Feature, Feature]] = {}
        self.window_index = None
        for i, w in enumerate(signature.params):
            if isinstance(w, StreamResolverParamMessageWindow):
                self.window_index = i
                break

        for window_period in self.window_periods_seconds:
            self.windowed_pseudofeatures[window_period] = {}
            for o in _flatten_features(self.output):
                if o.is_windowed:
                    windowed_fqn = get_name_with_duration(o.root_fqn, window_period)
                    windowed_feature = Feature.from_root_fqn(windowed_fqn)
                    self.windowed_pseudofeatures[window_period][o] = windowed_feature

    @property
    def output_features(self) -> Sequence[Feature]:
        return _flatten_features(self.output)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        from chalk._autosql.autosql import query_as_feature_formatted

        raw_result = self.fn(*args, **kwargs)
        if self.window_index is not None and isinstance(raw_result, str) and str(args[self.window_index]) in raw_result:
            raw_result = DataFrame(
                query_as_feature_formatted(
                    formatted_query=raw_result,
                    fqn_to_name={s.root_fqn: s.name for s in self.output_features},
                    table=args[self.window_index],
                )
            )

        return cast(T, raw_result)

    def __repr__(self):
        return f"StreamResolver(name={self.fqn})"


def _is_stream_resolver_body_type(annotation: Type):
    origin = get_origin(annotation)
    if origin is not None:
        return False
    return (
        isinstance(annotation, type) and issubclass(annotation, (str, bytes, BaseModel))
    ) or dataclasses.is_dataclass(annotation)


def _parse_stream_resolver_param(
    param: Parameter,
    annotation_parser: ResolverAnnotationParser,
    resolver_fqn_for_errors: str,
    is_windowed_resolver: bool,
) -> StreamResolverParam:
    if param.kind not in {Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD}:
        raise ValueError(
            f"Stream resolver '{resolver_fqn_for_errors}' includes unsupported keyword or variadic arg '{param.name}'"
        )

    annotation = annotation_parser.parse_annotation(param.name)
    if isinstance(annotation, StateWrapper):
        if is_windowed_resolver:
            raise ValueError(
                f"Windowed stream resolvers cannot have state, but '{resolver_fqn_for_errors}' requires state."
            )
        default_value = get_state_default_value(
            state_typ=annotation.typ,
            declared_default=param.default,
            resolver_fqn_for_errors=resolver_fqn_for_errors,
            parameter_name_for_errors=param.name,
        )
        return StreamResolverParamKeyedState(
            name=param.name,
            typ=annotation.typ,
            default_value=default_value,
        )

    if not is_windowed_resolver and _is_stream_resolver_body_type(annotation):
        return StreamResolverParamMessage(name=param.name, typ=annotation)

    if is_windowed_resolver and get_origin(annotation) in (list, List):
        item_typ = get_args(annotation)[0]
        if _is_stream_resolver_body_type(item_typ):
            return StreamResolverParamMessageWindow(name=param.name, typ=annotation)

    if (
        is_windowed_resolver
        and isclass(annotation)
        and (
            issubclass(annotation, pyarrow.Table)
            or issubclass(annotation, BaseModel)
            or annotation.__name__ in ("DataFrame", "DataFrameImpl", "SubclassedDataFrame")
        )
    ):
        # Using string comparison as polars may not be installed
        return StreamResolverParamMessageWindow(name=param.name, typ=annotation)

    raise ValueError(
        (
            f"Stream resolver parameter '{param.name}' of resolver '{resolver_fqn_for_errors}' is not recognized. "
            f"Message payloads must be one of `str`, `bytes`, or pydantic model class. "
            f"Keyed state parameters must be chalk.KeyedState[T]. "
            f"Received: {annotation}"
        )
    )


def _parse_stream_resolver_params(
    user_func: Callable,
    *,
    resolver_fqn_for_errors: str,
    annotation_parser: ResolverAnnotationParser,
    is_windowed_resolver: bool,
) -> Sequence[StreamResolverParam]:
    sig = inspect.signature(user_func)
    params = [
        _parse_stream_resolver_param(p, annotation_parser, resolver_fqn_for_errors, is_windowed_resolver)
        for p in sig.parameters.values()
    ]

    uses_message_body = any(
        p for p in params if isinstance(p, (StreamResolverParamMessage, StreamResolverParamMessageWindow))
    )

    if not uses_message_body:
        raise ValueError(
            f"Stream resolver '{resolver_fqn_for_errors}' must take as input "
            + f"a pydantic model, `str`, or `bytes` representing the message body"
        )

    keyed_state_params = [p.name for p in params if isinstance(p, StreamResolverParamKeyedState)]
    if len(keyed_state_params) > 1:
        raise ValueError(
            f"Stream resolver '{resolver_fqn_for_errors}' includes more than one KeyedState parameter: {keyed_state_params}"
        )

    return params


def _parse_stream_resolver_output_features(
    user_func: Callable,
    *,
    resolver_fqn_for_errors: str,
) -> Type[Features]:
    return_annotation = cached_get_type_hints(user_func).get("return")
    if return_annotation is None:
        raise TypeError(
            (
                f"Resolver '{user_func.__name__}' must have a return annotation. See "
                f"https://docs.chalk.ai/docs/resolver-outputs for "
                f"more information."
            )
        )

    if not isinstance(return_annotation, type):
        raise TypeError(f"return_annotation {return_annotation} of type {type(return_annotation)} is not a type")

    if issubclass(return_annotation, DataFrame):
        return Features[return_annotation]

    if not issubclass(return_annotation, Features):
        raise ValueError(
            f"Stream resolver '{resolver_fqn_for_errors}' did not have a valid return type: "
            + f"must be a features class or chalk.features.Features[]"
        )

    # TODO: validate that these features are in the same namespace and include a pkey
    output_features = cast(Type[Features], return_annotation)

    return output_features


@dataclass
class ParseInfo(Generic[T, V]):
    fn: Callable[[T], V]
    input_type: Type[T]
    output_type: Type[V]
    output_is_optional: bool


def _validate_parse_function(
    stream_fn: Callable[P, T],
    parse_fn: Callable[[T], V],
    globals: Optional[Dict[str, Any]],
    locals: Optional[Dict[str, Any]],
) -> ParseInfo:
    # check inputs and outputs
    stream_fqn = get_resolver_fqn(function=stream_fn)
    parse_fqn = get_resolver_fqn(function=parse_fn)
    sig = inspect.signature(parse_fn)
    annotation_parser = ResolverAnnotationParser(parse_fn, globals, locals)

    output_optional = False
    return_annotation = cached_get_type_hints(parse_fn).get("return")
    if not return_annotation:
        raise TypeError(f"Parse function '{parse_fqn}' must have a return annotation.")
    if get_origin(return_annotation) in (UnionType, Union):
        return_args = get_args(return_annotation)
        parse_output = next((a for a in return_args if a is not type(None)), None)
        if len(return_args) != 2 or type(None) not in return_args or parse_output is None:
            raise TypeError(
                (
                    f"Parse function '{parse_fqn}' return annotation of length '{len(return_args)}' must be of length one "
                    f"(Optional is supported) "
                )
            )
        output_optional = True
    elif get_origin(return_annotation):
        raise TypeError(
            f"Parse function '{parse_fqn}' return annotation {return_annotation} must be either Optional or a singleton."
        )
    else:
        parse_output = return_annotation
    if not issubclass(parse_output, BaseModel):
        raise TypeError(f"Parse function '{parse_fqn}' return annotation must be of type pydantic.BaseModel")
    stream_fn_inputs = inspect.signature(stream_fn).parameters
    stream_input_annotations = [param.annotation for param in stream_fn_inputs.values()]
    if len(stream_input_annotations) != 1:
        raise TypeError(
            (
                f"Streaming resolver '{stream_fqn}' of length '{len(stream_input_annotations)}' must have "
                f"one input argument"
            )
        )
    stream_input_annotation = stream_input_annotations[0]
    if get_origin(stream_input_annotation) in (List, list):
        stream_input_args = get_args(stream_input_annotation)
        stream_input_arg = next((a for a in stream_input_args if a is not type(None)), None)
        if len(stream_input_args) != 1 or stream_input_arg is None:
            raise TypeError(
                (
                    f"Streaming resolver '{stream_fqn}' input annotation of length '{len(stream_input_args)}' must be of "
                    f"length one (List or DataFrame supported) "
                )
            )
    elif isinstance(stream_input_annotation, DataFrameMeta):
        stream_input_annotation = cast(Type[DataFrame], stream_input_annotation)
        stream_input_arg = stream_input_annotation.__pydantic_model__
    else:
        stream_input_arg = stream_input_annotation
    if parse_output != stream_input_arg:
        raise TypeError(
            f"Parse function '{parse_fqn}' return annotation must match input annotation of resolver '{stream_fqn}'"
        )

    parse_inputs = [annotation_parser.parse_annotation(p) for p in sig.parameters.keys()]
    if len(parse_inputs) != 1:
        raise TypeError(f"Parse function '{parse_fqn}' of length '{len(parse_inputs)}' must have one input argument")
    parse_input = parse_inputs[0]
    if get_origin(parse_input):
        raise TypeError(f"Parse function '{parse_fqn}' input annotation must be a singleton")

    if not issubclass(parse_input, BaseModel) and parse_input != bytes:
        raise TypeError(f"Parse function '{parse_fqn}' input annotation must be of type pydantic.BaseModel or bytes")

    return ParseInfo(fn=parse_fn, input_type=parse_input, output_type=parse_output, output_is_optional=output_optional)


def _get_windowed_stream_resolver_input_type(stream_fn: Callable[P, T]) -> Type[BaseModel]:
    stream_fqn = get_resolver_fqn(function=stream_fn)
    stream_fn_inputs = inspect.signature(stream_fn).parameters
    stream_input_annotations = [param.annotation for param in stream_fn_inputs.values()]
    assert len(stream_input_annotations) == 1, "stream resolvers take in only one input"
    stream_input_type = stream_input_annotations[0]

    if get_origin(stream_input_type) in (List, list):
        input_model_types = get_args(stream_input_type)
        input_model_type = next((a for a in input_model_types if a is not type(None)), None)
    elif isinstance(stream_input_type, DataFrameMeta):
        stream_input_annotation = cast(Type[DataFrame], stream_input_type)
        input_model_type = stream_input_annotation.__pydantic_model__
    else:
        raise TypeError(f"Stream resolver '{stream_fqn}' inputs must be a list or a DataFrame")
    if not issubclass(input_model_type, BaseModel):
        raise TypeError(f"Stream resolver '{stream_fqn}' must take in BaseModels when using continuous mode and keys")
    return input_model_type


def _validate_keys(
    stream_fn: Callable[P, T],
    keys: Dict[str, Any],
) -> Dict[str, Any]:
    stream_fqn = get_resolver_fqn(function=stream_fn)

    if not isinstance(keys, dict):
        raise TypeError(f"Stream resolver '{stream_fqn}' keys parameter must be of type dict")
    input_model_type = _get_windowed_stream_resolver_input_type(stream_fn)

    return_annotation = cached_get_type_hints(stream_fn).get("return")
    if isinstance(return_annotation, FeaturesMeta):
        output_features = return_annotation.features
    elif isinstance(return_annotation, DataFrameMeta):
        output_features = return_annotation.columns
    else:
        raise TypeError(f"Stream resolver '{stream_fqn}' outputs must be Features or DataFrame")

    for key, value in keys.items():
        if not isinstance(key, str):
            raise TypeError(f"Stream resolver '{stream_fqn}' key '{key}' should be type string")
        if key not in input_model_type.__fields__.keys():
            raise ValueError(
                (
                    f"Stream resolver '{stream_fqn}' specifies an invalid 'key' mapping. "
                    f"Key '{key}' is not an attribute in input model class '{input_model_type}'"
                )
            )
        if not isinstance(value, FeatureWrapper):
            raise TypeError(
                (
                    f"Stream resolver '{stream_fqn}' maps key '{key}' to value '{value}', "
                    f"but '{value}' is not of type Feature"
                )
            )
        value = unwrap_feature(value)
        if not value.is_scalar:
            raise TypeError(
                (
                    f"Stream resolver '{stream_fqn}' maps key '{key}' to value '{value}', "
                    f"but '{value}' is not a scalar feature"
                )
            )
        if value not in output_features:
            output_fqns = [f.fqn for f in output_features]
            raise ValueError(
                (
                    f"Stream resolver '{stream_fqn}' specifies an invalid 'key' mapping: "
                    f"Key '{key}' is mapped to '{value}', but value '{value}' is not present"
                    f" in output features {output_fqns}"
                )
            )
    return {key: keys[key] for key in sorted(keys.keys())}


def _validate_timestamp(stream_fn: Callable[P, T], timestamp: str, source: StreamSource):
    stream_fqn = get_resolver_fqn(function=stream_fn)
    input_model_type = _get_windowed_stream_resolver_input_type(stream_fn)

    if timestamp not in input_model_type.__fields__.keys():
        raise ValueError(
            (
                f"Stream resolver '{stream_fqn}' specifies an invalid 'timestamp' attribute. "
                f"'{timestamp}' is not an attribute in input model class '{input_model_type}'"
            )
        )
    model_field = input_model_type.__fields__[timestamp]
    if model_field.type_ != datetime:
        raise TypeError(
            (
                f"Stream resolver '{stream_fqn}' specifies an invalid 'timestamp' attribute. "
                f"'{timestamp}' field must be of type datetime.datetime. "
                f"Use the parse function to convert your timestamp to a timezoned (not naive!) datetime."
            )
        )


def parse_and_register_stream_resolver(
    *,
    caller_globals: Optional[Dict[str, Any]],
    caller_locals: Optional[Dict[str, Any]],
    fn: Callable[P, T],
    source: StreamSource,
    caller_filename: str,
    mode: Optional[Literal["continuous", "tumbling"]] = None,
    environment: Optional[Union[List[str], str]] = None,
    machine_type: Optional[MachineType] = None,
    message: Optional[Type[Any]] = None,
    sql_query: Optional[str] = None,
    owner: Optional[str] = None,
    parse: Optional[Callable[[T], V]] = None,
    keys: Optional[Dict[str, Any]] = None,
    timestamp: Optional[str] = None,
) -> StreamResolver[P, T]:
    fqn = f"{fn.__module__}.{fn.__name__}"
    annotation_parser = ResolverAnnotationParser(fn, caller_globals, caller_locals)
    output_features = _parse_stream_resolver_output_features(
        fn,
        resolver_fqn_for_errors=fqn,
    )
    flattened_output_features = (
        df.columns
        if len(output_features.features) == 1
        and isinstance(output_features.features[0], type)
        and issubclass(df := output_features.features[0], DataFrame)
        else output_features.features
    )
    is_windowed_resolver = any(x.is_windowed for x in flattened_output_features)
    params = _parse_stream_resolver_params(
        fn,
        resolver_fqn_for_errors=fqn,
        annotation_parser=annotation_parser,
        is_windowed_resolver=is_windowed_resolver,
    )
    parse_info = None
    if parse:
        parse_info = _validate_parse_function(
            stream_fn=fn, parse_fn=parse, globals=caller_globals, locals=caller_locals
        )
    if keys is not None and mode == "continuous":
        keys = _validate_keys(stream_fn=fn, keys=keys)
    elif keys is None and mode == "continuous":
        raise ValueError(
            (
                f"Stream resolver '{fqn}' must take a 'keys' argument in the decorator "
                f"if mode is continuous. The 'keys' argument should be dict mapping from "
                f"the attribute of the incoming message to the Chalk feature"
            )
        )
    elif keys and not is_windowed_resolver:
        raise ValueError(
            (
                f"Stream resolver '{fqn}' takes in a 'keys' argument in the decorator "
                f"but is not a windowed resolver. Only windowed resolvers take in 'keys'."
            )
        )

    if isinstance(output_features.features[0], type) and issubclass(output_features.features[0], DataFrame):
        output_feature_fqns = set(f.fqn for f in cast(Type[DataFrame], output_features.features[0]).columns)
    else:
        output_feature_fqns = set(f.fqn for f in output_features.features)

    signature = StreamResolverSignature(
        params=params,
        output_feature_fqns=output_feature_fqns,
    )
    parsed = parse_function(fn, caller_globals, caller_locals, allow_custom_args=True, is_streaming_resolver=True)

    if timestamp and is_windowed_resolver:
        _validate_timestamp(stream_fn=fn, timestamp=timestamp, source=StreamSource)
    elif timestamp and not is_windowed_resolver:
        raise ValueError(
            (
                f"Stream resolver '{fqn}' takes in a 'timestamp' argument in the decorator "
                f"but is not a windowed resolver. Only windowed resolvers take in 'timestamp'."
            )
        )
    for resolver in StreamResolver.registry:
        if resolver.source == source:
            if resolver.timestamp != timestamp:
                raise ValueError(
                    (
                        f"Stream resolver '{fqn}' specifies 'timestamp' attribute, "
                        f"but stream resolver '{resolver.fqn}' does not or specifies a different attribute. "
                        f"Stream resolvers with the same source must all have the same timestamp value"
                    )
                )

    resolver = StreamResolver(
        function_definition=parsed.function_definition,
        fqn=parsed.fqn,
        filename=caller_filename,
        source=source,
        fn=fn,
        environment=None if environment is None else list(ensure_tuple(environment)),
        doc=parsed.doc,
        module=fn.__module__,
        mode=mode,
        machine_type=machine_type,
        message=message,
        output=output_features,
        signature=signature,
        state=parsed.state,
        sql_query=None,
        owner=owner,
        parse=parse_info,
        keys=keys,
        timestamp=timestamp,
    )

    StreamResolver.registry.append(resolver)
    return resolver
