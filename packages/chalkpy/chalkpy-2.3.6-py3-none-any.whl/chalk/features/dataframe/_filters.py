from __future__ import annotations

import collections.abc
import datetime
import enum
import functools
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Sequence, Union

from chalk.features.feature_field import Feature
from chalk.features.feature_wrapper import FeatureWrapper, unwrap_feature
from chalk.features.filter import Filter, TimeDelta
from chalk.utils.collections import ensure_tuple

if TYPE_CHECKING:
    import polars as pl


def convert_filters_to_pl_expr(
    filters: Sequence[Filter],
    df_schema: Mapping[str, pl.PolarsDataType],
    timestamp_feature: Optional[Feature] = None,
    now: Optional[datetime.datetime] = None,
):
    if len(filters) == 0:
        return None
    polars_filters = (_convert_filter_to_pl_expr(f, df_schema, timestamp_feature, now) for f in filters)
    return functools.reduce(lambda a, b: a & b, polars_filters)


def _convert_filter_to_pl_expr(
    f: Filter,
    df_schema: Mapping[str, pl.PolarsDataType],
    timestamp_feature: Optional[Feature] = None,
    now: Optional[datetime.datetime] = None,
) -> pl.Expr:
    """Convert filters to a polars expression

    Parameters
    ----------
    f
        The filter
    df_schema
        The DataFrame schema.
    timestamp_feature
        The feature corresponding to the observation time
    now
        The datetime to use for the current timestamp. Used to resolve relative
        timestamps in filters to absolute datetimes.
    Returns
    -------
    pl.Expr
        A series of boolean values that can be used to select the rows where the filter is truthy
    """
    import polars as pl

    # Passing `now` in explicitly instead of using datetime.datetime.now() so that multiple filters
    # relying on relative timestamps (e.g. before, after) will have the same "now" time.
    if f.operation == "not":
        assert f.rhs is None, "not has just one side"
        assert isinstance(f.lhs, Filter), "lhs must be a filter"
        return ~_convert_filter_to_pl_expr(f.lhs, df_schema, timestamp_feature, now)
    elif f.operation == "and":
        assert isinstance(f.rhs, Filter), "rhs must be a filter"
        assert isinstance(f.lhs, Filter), "lhs must be a filter"
        return _convert_filter_to_pl_expr(f.lhs, df_schema, timestamp_feature, now) & _convert_filter_to_pl_expr(
            f.rhs, df_schema, timestamp_feature, now
        )
    elif f.operation == "or":
        assert isinstance(f.rhs, Filter), "rhs must be a filter"
        assert isinstance(f.lhs, Filter), "lhs must be a filter"
        return _convert_filter_to_pl_expr(f.lhs, df_schema, timestamp_feature, now) | _convert_filter_to_pl_expr(
            f.rhs, df_schema, timestamp_feature, now
        )

    lhs = _parse_feature_or_value(f.lhs, timestamp_feature, now)
    rhs = _parse_feature_or_value(f.rhs, timestamp_feature, now)

    lhs_converter = None
    if isinstance(lhs, Feature):
        lhs_converter = lhs.converter
        lhs = pl.col(str(lhs))

    rhs_converter = None
    if isinstance(rhs, Feature):
        rhs_converter = rhs.converter
        rhs = pl.col(str(rhs))

    if lhs_converter is None:
        # LHS is literal. Encode it into the rhs_dtype
        assert rhs_converter is not None
        lhs = rhs_converter.from_rich_to_primitive(lhs)
    if rhs_converter is None:
        # RHS is literal. Encode it into the lhs_dtype
        assert lhs_converter is not None
        if f.operation in ("in", "not in"):
            assert isinstance(rhs, collections.abc.Iterable)
            rhs = [lhs_converter.from_rich_to_primitive(x) for x in rhs]
        else:
            rhs = lhs_converter.from_rich_to_primitive(rhs)

    if rhs is None:
        assert isinstance(lhs, pl.Expr)
        if f.operation == "==":
            return lhs.is_null()

        elif f.operation == "!=":
            return lhs.is_not_null()

    if f.operation in ("in", "not in"):
        assert lhs_converter is not None
        assert isinstance(lhs, pl.Expr)
        assert isinstance(rhs, collections.abc.Iterable)
        ret = _polars_is_in(lhs, rhs, lhs_converter.polars_dtype)
        if f.operation == "not in":
            ret = ~ret
    elif f.operation in ("==", "!="):
        ret = _polars_is_eq(
            lhs=lhs,
            rhs=rhs,
            lhs_dtype=None if lhs_converter is None else lhs_converter.polars_dtype,
            rhs_dtype=None if rhs_converter is None else rhs_converter.polars_dtype,
        )
        if f.operation == "!=":
            ret = ~ret
    elif f.operation == "!=":
        ret = lhs != rhs
    elif f.operation == ">=":
        ret = lhs >= rhs
    elif f.operation == ">":
        ret = lhs > rhs
    elif f.operation == "<":
        ret = lhs < rhs
    elif f.operation == "<=":
        ret = lhs <= rhs
    else:
        raise ValueError(f'Unknown operation "{f.operation}"')
    assert isinstance(ret, pl.Expr)
    return ret


def _feature_type_or_value(e: Union[Feature, FeatureWrapper]):
    if isinstance(e, FeatureWrapper):
        e = unwrap_feature(e)
    return e


def _maybe_replace_timestamp_feature(f: Union[Feature, Any], observed_at_feature: Optional[Feature]):
    """Replace the ``CHALK_TS`` pseudo-feature with the actual timestamp column."""
    if not isinstance(f, Feature) or f.fqn != "__chalk__.CHALK_TS":
        return f
    if observed_at_feature is not None:
        return observed_at_feature
    raise ValueError("No Timestamp Feature Found")


def _maybe_convert_timedelta_to_timestamp(
    f: Union[TimeDelta, datetime.timedelta, Any], now: Optional[datetime.datetime]
):
    """Convert timedeltas relative to ``now`` into absolute datetimes."""
    if isinstance(f, TimeDelta):
        f = f.to_std()
    if isinstance(f, datetime.timedelta):
        if now is None:
            raise ValueError(
                "The filter contains a relative timestamp. The current datetime must be provided to evaluate this filter."
            )
        return now + f
    return f


def _parse_feature_or_value(
    f: Union[Feature, Any], timestamp_feature: Optional[Feature], now: Optional[datetime.datetime]
):
    """Parse a feature or value into the correct type that can be used for filtering."""
    f = _feature_type_or_value(f)
    f = _maybe_convert_timedelta_to_timestamp(f, now)
    f = _maybe_replace_timestamp_feature(f, timestamp_feature)
    if isinstance(f, enum.Enum):
        f = f.value
    return f


def _polars_is_in(lhs: pl.Expr, rhs: Sequence, lhs_dtype: pl.PolarsDataType):
    """Filter for where the lhs is in the RHS. The RHS must be a literal collection."""
    import polars as pl

    if isinstance(lhs_dtype, pl.Struct):
        # Assert equality field by field
        filters = []
        rhs_by_fields: Dict[str, List[Any]] = {}
        for item in rhs:
            for field in lhs_dtype.fields:
                if field.name not in rhs_by_fields:
                    rhs_by_fields[field.name] = []
                # Assuming that struct-like objects make their members accessible by attribute name or __getitem__
                try:
                    rhs_vector = getattr(item, field.name)
                except AttributeError:
                    rhs_vector = item[field.name]
                rhs_by_fields[field.name].append(rhs_vector)
        for field in lhs_dtype.fields:
            field_name = field.name
            new_lhs = lhs.struct.field(field_name)
            new_lhs_dtype = field.dtype
            new_rhs = rhs_by_fields[field_name]
            filters.append(_polars_is_in(new_lhs, new_rhs, new_lhs_dtype))
        assert len(filters) > 0, "structs with 0 fields are unsupported"
        return functools.reduce(lambda a, b: a & b, filters)
    if not isinstance(lhs_dtype, type):
        lhs_dtype = type(lhs_dtype)
    return lhs.is_in(pl.lit(pl.Series(values=rhs, dtype=lhs_dtype), allow_object=True))


def _polars_is_eq(
    lhs: Any,
    rhs: Any,
    lhs_dtype: Optional[pl.PolarsDataType],
    rhs_dtype: Optional[pl.PolarsDataType],
):
    """Compare a column with another column or literal value, including possibly a struct.
    Polars does not permit equality comparisons on structs directly. Instead, must compare field by field, potentially recursively.
    """
    import polars as pl

    if rhs_dtype is not None:
        if lhs_dtype is None:
            # Swap the columns
            return _polars_is_eq(rhs, lhs, rhs_dtype, lhs_dtype)
        else:
            # Comparing two columns
            assert isinstance(lhs, pl.Expr)
            assert isinstance(rhs, pl.Expr)
            if isinstance(lhs_dtype, pl.Struct):
                assert isinstance(rhs_dtype, pl.Struct)
                # Assert equality field by field
                filters = []
                for field in lhs_dtype.fields:
                    field_name = field.name
                    new_lhs = lhs.struct.field(field_name)
                    new_lhs_dtype = field.dtype
                    new_rhs = rhs.struct.field(field_name)
                    new_rhs_dtype = field.dtype
                    filters.append(_polars_is_eq(new_lhs, new_rhs, new_lhs_dtype, new_rhs_dtype))
                assert len(filters) > 0, "structs with 0 fields are unsupported"
                return functools.reduce(lambda a, b: a & b, filters)
            return lhs == rhs
    # rhs is literal
    # lhs is a column
    assert lhs_dtype is not None, "one side must be a column"
    assert isinstance(lhs, pl.Expr)
    if isinstance(lhs_dtype, pl.Struct):
        # Assert equality field by field
        filters = []
        for field in lhs_dtype.fields:
            field_name = field.name
            new_lhs = lhs.struct.field(field_name)
            new_lhs_dtype = field.dtype
            # Assuming that struct-like objects make their members accessible by attribute name or __getitem__
            try:
                new_rhs = getattr(rhs, field_name)
            except AttributeError:
                new_rhs = rhs[field_name]
            new_rhs_dtype = None  # literal values do not have dtypes
            filters.append(_polars_is_eq(new_lhs, new_rhs, new_lhs_dtype, new_rhs_dtype))
        assert len(filters) > 0, "structs with 0 fields are unsupported"
        return functools.reduce(lambda a, b: a & b, filters)
    if not isinstance(lhs_dtype, type):
        lhs_dtype = type(lhs_dtype)
    assert issubclass(lhs_dtype, pl.DataType)
    return lhs == pl.lit(rhs, dtype=lhs_dtype, allow_object=True)


def filter_data_frame(
    item: Any,
    underlying: Union[pl.DataFrame, pl.LazyFrame],
    namespace: Optional[str],
) -> Union[pl.DataFrame, pl.LazyFrame]:
    # Use the Chalk projection / selection syntax, where we support our Filter objects and
    # selection by column name
    from chalk.features.feature_set import FeatureSetBase

    projections: list[str] = []
    filters: List[Filter] = []
    for x in ensure_tuple(item):
        if isinstance(x, (FeatureWrapper, Feature, str)):
            projections.append(str(x))

        elif isinstance(x, Filter):
            filters.append(x)
        else:
            raise TypeError(
                "When indexing by Filters or Features, it is not simultaneously possible to perform other indexing operations."
            )

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    timestamp_feature = None if namespace is None else FeatureSetBase.registry[namespace].__chalk_ts__
    pl_expr = convert_filters_to_pl_expr(filters, underlying.schema, timestamp_feature, now)
    df = underlying
    if pl_expr is not None:
        df = df.filter(pl_expr)
    # Do the projection
    if len(projections) > 0:
        polars_cols_set = set(df.columns)
        missing_cols = [c for c in projections if c not in polars_cols_set]
        if len(missing_cols) > 0:
            raise KeyError(f"Attempt to select missing columns {missing_cols}")

        df = df.select(projections)
    return df
