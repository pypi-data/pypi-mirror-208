from __future__ import annotations

from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class Validation(Generic[T]):
    def __init__(
        self,
        min: Optional[T] = None,
        max: Optional[T] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        strict: bool = False,
    ):
        """Specify explicit validations to use for a feature.

        The `feature()` function can also specify these validations,
        but this class allows you to specify both strict and non-strict
        validations at the same time.

        Parameters
        ----------
        min
            If specified, when this feature is computed, Chalk will check that `x >= min`.
        max
            If specified, when this feature is computed, Chalk will check that `x <= max`.
        min_length
            If specified, when this feature is computed, Chalk will check that `len(x) >= min_length`.
        max_length
            If specified, when this feature is computed, Chalk will check that `len(x) <= max_length`.
        strict
            If `True`, if this feature does not meet the validation criteria, Chalk will not persist
            the feature value and will treat it as failed.

        Examples
        --------
        >>> from chalk.features import features, feature
        >>> @features
        ... class User:
        ...     fico_score: int = feature(
        ...         validations=[
        ...             Validation(min=300, max=850, strict=True),
        ...             Validation(min=300, max=320, strict=False),
        ...             Validation(min=840, max=850, strict=False),
        ...         ]
        ...     )
        """
        self.min = min
        self.max = max
        self.min_length = min_length
        self.max_length = max_length
        self.strict = strict
