import abc
from typing import List, Optional, Type, cast

from chalk.client.models import ChalkError


class ChalkBaseException(Exception, abc.ABC):
    """The base type for Chalk exceptions.

    This exception makes error handling easier, as you can
    look only for this exception class.
    """

    errors: List[ChalkError]
    """The errors from executing a Chalk operation.

    These errors contain more detailed information about
    why the exception occurred.
    """

    def __init__(self, errors: Optional[List[ChalkError]] = None, trace_id: Optional[str] = None):
        if errors is None:
            errors = []

        self.errors = errors
        self.trace_id = trace_id

        super().__init__(self.full_message)

    @property
    def message(self) -> str:
        """A message describing the specific type of exception raised."""
        raise NotImplementedError

    @property
    def full_message(self) -> str:
        """A message that describes the specific type of exception raised
        and contains the readable representation of each error in the
        errors attribute.
        """
        if self.errors:
            return self.message + "\n" + "\n".join(["\t" + e.message for e in self.errors])

        return self.message


def _generate_chalk_exception_class(name: str, message: str) -> Type[ChalkBaseException]:
    new_exception_cls = type(
        name,
        (ChalkBaseException,),
        {
            "message": message,
        },
    )
    return cast(Type[ChalkBaseException], new_exception_cls)


def _generic_chalk_exception(message: str) -> Type[ChalkBaseException]:
    return _generate_chalk_exception_class("ChalkException", message)


class ChalkCustomException(ChalkBaseException):
    def __init__(self, message: str, errors: Optional[List[ChalkError]] = None):
        self._message = message
        super().__init__(errors=errors)

    @property
    def message(self) -> str:
        return self._message


class ChalkWhoAmIException(ChalkBaseException):
    """Raised from the `ChalkClient.whoami` method."""

    @property
    def message(self) -> str:
        return "Failed to retrieve current user information during `whoami` check"


class ChalkOnlineQueryException(ChalkBaseException):
    @property
    def message(self) -> str:
        return "Failed to execute online query"


class ChalkOfflineQueryException(ChalkBaseException):
    @property
    def message(self) -> str:
        return "Failed to execute offline query"

    @property
    def full_message(self) -> str:
        msg = self.message
        if self.errors:
            for e in self.errors:
                msg += f"\n\n{e.message}"
                if e.exception:
                    msg += f"\n{e.exception.stacktrace}"
                    msg += f"\n{e.exception.message}"
        return msg


class ChalkComputeResolverException(ChalkOfflineQueryException):
    """Exception raised when failing to compute the resolver output."""

    @property
    def message(self) -> str:
        return "Failed to compute resolver output"


class ChalkResolverRunException(ChalkBaseException):
    """Raised when failing to get the resolver's status via `ChalkClient.get_run_status`"""

    @property
    def message(self) -> str:
        return "Resolver run failed"


class ChalkUpdateGraphEntityException(ChalkBaseException):
    """Raised when failing to update a resolver or feature on the fly from a notebook"""

    @property
    def message(self) -> str:
        return "Failed to update resolver or feature."


class ChalkUpdateResolverException(ChalkBaseException):
    """Raised when failing to update a resolver on the fly from a notebook"""

    @property
    def message(self) -> str:
        return "Failed to update resolver."


class ChalkGetBatchReportException(ChalkBaseException):
    def __init__(self, operation_id: str, errors: Optional[List[ChalkError]] = None):
        self.operation_id = operation_id
        super().__init__(errors)

    @property
    def message(self) -> str:
        return f"Failed to get status of operation with id '{self.operation_id}'"


class ChalkGetDatasetException(ChalkBaseException):
    def __init__(self, revision_id: str, errors: Optional[List[ChalkError]] = None):
        self.revision_id = revision_id
        super().__init__(errors)

    @property
    def message(self) -> str:
        return f"Failed to get dataset for revision id '{self.revision_id}'"


class ChalkRecomputeDatasetException(ChalkBaseException):
    def __init__(self, dataset_name: Optional[str] = None, errors: Optional[List[ChalkError]] = None):
        self.dataset_name = dataset_name
        super().__init__(errors)

    @property
    def message(self) -> str:
        return (
            (
                f"Failed to recompute dataset '{self.dataset_name}'"
                if self.dataset_name
                else "Failed to recompute anonymous dataset"
            )
            + "\n"
            + "\n".join(["\t" + e.message for e in self.errors])
        )


class ChalkDatasetDownloadException(ChalkBaseException):
    def __init__(self, dataset_name: str, errors: Optional[List[ChalkError]] = None):
        self.dataset_name = dataset_name
        super().__init__(errors)

    @property
    def message(self) -> str:
        return f"Failed to download dataset '{self.dataset_name}'"

    @property
    def full_message(self) -> str:
        return self.message + "\n" + "\n".join(["\t" + e.message for e in self.errors])


class ChalkAuthException(ChalkBaseException):
    """Raised when constructing a `ChalkClient` without valid credentials.

    When this exception is raise, no explicit `client_id` and `client_secret`
    were provided, there was no `~/.chalk.yml` file with applicable credentials,
    and the environment variables `CHALK_CLIENT_ID` and `CHALK_CLIENT_SECRET`
    were not set.

    You may need to run `chalk login` from your command line, or check that your
    working directory is set to the root of your project.
    """

    @property
    def message(self):
        return (
            "Explicit `client_id` and `client_secret` are not provided, "
            "there is no `~/.chalk.yml` file with applicable credentials, "
            "and the environment variables `CHALK_CLIENT_ID` and "
            "`CHALK_CLIENT_SECRET` are not set. "
            "You may need to run `chalk login` from your command line, "
            "or check that your working directory is set to the root of "
            "your project."
        )


__all__ = [
    "ChalkBaseException",
    "ChalkCustomException",
    "ChalkOnlineQueryException",
    "ChalkOfflineQueryException",
    "ChalkResolverRunException",
    "ChalkDatasetDownloadException",
    "ChalkComputeResolverException",
    "ChalkUpdateGraphEntityException",
    "ChalkAuthException",
    "ChalkWhoAmIException",
]
