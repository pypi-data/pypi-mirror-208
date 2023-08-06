from typing import Any, Type, TypeVar, cast

from typing_extensions import Annotated

from chalk.features.feature_wrapper import unwrap_feature

T = TypeVar("T")


class PrimaryMeta(type):
    def __getitem__(self, item: Type[T]) -> Type[T]:
        return cast(Type[T], Annotated[item, "__chalk_primary__"])


Primary = PrimaryMeta("Primary", (object,), {})
"""Marks a feature as the primary feature for a feature class.

Features named `id` on feature classes without an explicit primary
feature are declared primary keys by default, and don't need to be
marked with `Primary`.

If you have primary key feature with a name other than `id`,
you can use this marker to indicate the primary key.

Examples
--------
>>> @features
... class User:
...     uid: Primary[int]
"""


def is_primary(f: Any) -> bool:
    """Determine whether a feature is a primary key.

    Parameters
    ----------
    f
        A feature (i.e. `User.email`)

    Raises
    ------
    TypeError
        If `f` is not a feature.

    Returns
    -------
    bool
        `True` if `f` is primary and `False` otherwise.

    Examples
    --------
    >>> from chalk.features import features
    >>> @features
    ... class User:
    ...     uid: Primary[int]
    ...     email: str
    >>> assert is_primary(User.uid)
    >>> assert not is_primary(User.email)
    """
    return unwrap_feature(f).primary
