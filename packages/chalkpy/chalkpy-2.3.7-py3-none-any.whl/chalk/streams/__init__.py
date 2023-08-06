import inspect
from typing import Any, Callable, Dict, Literal, Optional, TypeVar

from typing_extensions import ParamSpec

from chalk.features.tag import Environments
from chalk.state import KeyedState
from chalk.streams._file_source import FileSource
from chalk.streams._kafka_source import KafkaSource
from chalk.streams._windows import Windowed, get_duration_secs, get_name_with_duration, windowed
from chalk.streams.base import StreamSource
from chalk.utils import AnyDataclass, MachineType

__all__ = [
    "FileSource",
    "KafkaSource",
    "KeyedState",
    "StreamSource",
    "Windowed",
    "stream",
    "windowed",
    "get_name_with_duration",
    "get_duration_secs",
]

P = ParamSpec("P")
T = TypeVar("T")
V = TypeVar("V")


def stream(
    *,
    source: StreamSource,
    mode: Optional[Literal["continuous", "tumbling"]] = None,
    environment: Optional[Environments] = None,
    machine_type: Optional[MachineType] = None,
    message: Optional[AnyDataclass] = None,
    owner: Optional[str] = None,
    parse: Optional[Callable[[T], V]] = None,
    keys: Optional[Dict[str, Any]] = None,
    timestamp: Optional[str] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to create a stream resolver.

    Parameters
    ----------
    source
        The streaming source, e.g. `KafkaSource()`.
    mode
        Tumbling windows are fixed-size, contiguous and non-overlapping time intervals. You can think of
        tumbling windows as adjacently arranged bins of equal width.
        Tumbling windows are most often used alongside `max_staleness` to allow the features
        to be sent to the online store and offline store after each window period.

        Continuous windows, unlike tumbling window, are overlapping and exact.
        When you request the value of a continuous window feature, Chalk looks
        at all the messages received in the window and computes the value on-demand.

        See more at https://docs.chalk.ai/docs/aggregations#window-modes
    environment
        Environments are used to trigger behavior in different deployments
        such as staging, production, and local development.

        Environment can take one of three types:
            - `None` (default) - candidate to run in every environment
            - `str` - run only in this environment
            - `list[str]` - run in any of the specified environment and no others

        Read more at https://docs.chalk.ai/docs/resolver-environments
    message
        The type of the message on a stream.

        You can use any `dataclass`. The message on your stream is assumed
        to be Json that matches the schema provided by the `dataclass`.
        Note that Chalk does not use `dataclass` in practice to deserialize
        the data, but instead derives a `pyarrow.Schema` that mirrors the
        `dataclass`.
    owner
        Individual or team responsible for this resolver.
        The Chalk Dashboard will display this field, and alerts
        can be routed to owners.
    parse
        A callable that will interpret an input prior to the invocation of the resolver
    keys
        A mapping from input attribute to features to support continuous streaming re-keying
    timestamp
        An optional string specifying an input attribute as the timestamp used for windowed aggregations

    Other Parameters
    ----------------
    machine_type
        You can optionally specify that resolvers need to run
        on a machine other than the default. Must be configured
        in your deployment.

    Returns
    -------
    Callable[[Any, ...], Any]
        A callable function! You can unit-test resolvers as you would
        unit-test any other code.

        Read more at https://docs.chalk.ai/docs/unit-tests
    """
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename
    caller_globals = caller_frame.frame.f_globals
    caller_locals = caller_frame.frame.f_locals
    from chalk.features.resolver import parse_and_register_stream_resolver

    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        return parse_and_register_stream_resolver(
            caller_globals=caller_globals,
            caller_locals=caller_locals,
            fn=fn,
            source=source,
            mode=mode,
            caller_filename=caller_filename,
            environment=environment,
            machine_type=machine_type,
            message=message,
            owner=owner,
            parse=parse,
            keys=keys,
            timestamp=timestamp,
        )

    return decorator
