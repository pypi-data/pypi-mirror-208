# AUTO-GENERATED FILE. Do not edit.
from typing import Any, Dict, List, Literal, Optional, Tuple, TypeVar, Union

from chalk._monitoring.charts_enums_codegen import GroupByKind
from chalk._monitoring.charts_series_base import ResolverType, SeriesBase
from chalk.features.resolver import ResolverProtocol


class Series(SeriesBase):
    """
    Class describing a series of data in two dimensions, as in a line chart.
    Series should be instantiated with one of the classmethods that specifies
    the metric to be tracked.
    """

    def __new__(cls, *args, **kwargs):
        raise ValueError("Please construct a Series with a metric classmethod")

    @classmethod
    def feature_request_count_metric(cls, name: str) -> "FeatureRequestCountSeries":
        """Creates a Series of metric kind FeatureRequestCount.

        Parameters
        ----------
        name
            A name for your new `feature_request_count` Series.

        Returns
        -------
        FeatureRequestCountSeries
            A new `FeatureRequestCountSeries` instance that inherits from the `Series` class.
        """
        return FeatureRequestCountSeries(name=name, metric="FEATURE_REQUEST_COUNT", window_function="COUNT")

    @classmethod
    def feature_staleness_metric(
        cls,
        name: str,
        window_function: Literal["count", "mean", "sum", "max", "99%", "95%", "75%", "50%", "25%", "5%", "min", "all"],
    ) -> "FeatureStalenessSeries":
        """Creates a Series of metric kind `FeatureStaleness`.

        Parameters
        ----------
        name
            A name for your new `feature_staleness` Series.
        window_function
            The time window to calculate the metric over.

        Returns
        -------
        FeatureStalenessSeries
            A new `FeatureStalenessSeries` instance that inherits from the `Series` class.
        """
        if window_function not in {
            "count",
            "mean",
            "sum",
            "max",
            "99%",
            "95%",
            "75%",
            "50%",
            "25%",
            "5%",
            "min",
            "all",
        }:
            raise ValueError(f"window_function value '{window_function}' is not valid")
        return FeatureStalenessSeries(name=name, metric="FEATURE_STALENESS", window_function=window_function)

    @classmethod
    def feature_value_metric(
        cls,
        name: str,
        window_function: Literal["mean", "sum", "max", "99%", "95%", "75%", "50%", "25%", "5%", "min", "all"],
    ) -> "FeatureValueSeries":
        """Creates a Series of metric kind `FeatureValue`.

        Parameters
        ----------
        name
            A name for your new `feature_value` Series.
        window_function
            The time window to calculate the metric over.

        Returns
        -------
        FeatureValueSeries
            A new `FeatureValueSeries` instance that inherits from the `Series` class.
        """
        if window_function not in {"mean", "sum", "max", "99%", "95%", "75%", "50%", "25%", "5%", "min", "all"}:
            raise ValueError(f"window_function value '{window_function}' is not valid")
        return FeatureValueSeries(name=name, metric="FEATURE_VALUE", window_function=window_function)

    @classmethod
    def feature_null_ratio_metric(cls, name: str) -> "FeatureNullRatioSeries":
        """Creates a Series of metric kind `FeatureNullRatio`.

        Parameters
        ----------
        name
            A name for your new `feature_null_ratio` Series.

        Returns
        -------
        FeatureNullRatioSeries
            A new `FeatureNullRatioSeries` instance that inherits from the `Series` class.
        """
        return FeatureNullRatioSeries(
            name=name,
            metric="FEATURE_NULL_RATIO",
        )

    @classmethod
    def resolver_request_count_metric(cls, name: str) -> "ResolverRequestCountSeries":
        """Creates a Series of metric kind ResolverRequestCount.

        Parameters
        ----------
        name
            A name for your new `resolver_request_count` Series.

        Returns
        -------
        ResolverRequestCountSeries
            A new `ResolverRequestCountSeries` instance that inherits from the `Series` class.
        """
        return ResolverRequestCountSeries(name=name, metric="RESOLVER_REQUEST_COUNT", window_function="COUNT")

    @classmethod
    def resolver_latency_metric(
        cls,
        name: str,
        window_function: Literal["count", "mean", "sum", "max", "99%", "95%", "75%", "50%", "25%", "5%", "min", "all"],
    ) -> "ResolverLatencySeries":
        """Creates a Series of metric kind `ResolverLatency`.

        Parameters
        ----------
        name
            A name for your new `resolver_latency` Series.
        window_function
            The time window to calculate the metric over.

        Returns
        -------
        ResolverLatencySeries
            A new `ResolverLatencySeries` instance that inherits from the `Series` class.
        """
        if window_function not in {
            "count",
            "mean",
            "sum",
            "max",
            "99%",
            "95%",
            "75%",
            "50%",
            "25%",
            "5%",
            "min",
            "all",
        }:
            raise ValueError(f"window_function value '{window_function}' is not valid")
        return ResolverLatencySeries(name=name, metric="RESOLVER_LATENCY", window_function=window_function)

    @classmethod
    def resolver_success_ratio_metric(cls, name: str) -> "ResolverSuccessRatioSeries":
        """Creates a Series of metric kind `ResolverSuccessRatio`.

        Parameters
        ----------
        name
            A name for your new `resolver_success_ratio` Series.

        Returns
        -------
        ResolverSuccessRatioSeries
            A new `ResolverSuccessRatioSeries` instance that inherits from the `Series` class.
        """
        return ResolverSuccessRatioSeries(
            name=name,
            metric="RESOLVER_SUCCESS_RATIO",
        )

    @classmethod
    def query_count_metric(cls, name: str) -> "QueryCountSeries":
        """Creates a Series of metric kind QueryCount.

        Parameters
        ----------
        name
            A name for your new `query_count` Series.

        Returns
        -------
        QueryCountSeries
            A new `QueryCountSeries` instance that inherits from the `Series` class.
        """
        return QueryCountSeries(name=name, metric="QUERY_COUNT", window_function="COUNT")

    @classmethod
    def query_latency_metric(
        cls,
        name: str,
        window_function: Literal["count", "mean", "sum", "max", "99%", "95%", "75%", "50%", "25%", "5%", "min", "all"],
    ) -> "QueryLatencySeries":
        """Creates a Series of metric kind `QueryLatency`.

        Parameters
        ----------
        name
            A name for your new `query_latency` Series.
        window_function
            The time window to calculate the metric over.

        Returns
        -------
        QueryLatencySeries
            A new `QueryLatencySeries` instance that inherits from the `Series` class.
        """
        if window_function not in {
            "count",
            "mean",
            "sum",
            "max",
            "99%",
            "95%",
            "75%",
            "50%",
            "25%",
            "5%",
            "min",
            "all",
        }:
            raise ValueError(f"window_function value '{window_function}' is not valid")
        return QueryLatencySeries(name=name, metric="QUERY_LATENCY", window_function=window_function)

    @classmethod
    def query_success_ratio_metric(cls, name: str) -> "QuerySuccessRatioSeries":
        """Creates a Series of metric kind `QuerySuccessRatio`.

        Parameters
        ----------
        name
            A name for your new `query_success_ratio` Series.

        Returns
        -------
        QuerySuccessRatioSeries
            A new `QuerySuccessRatioSeries` instance that inherits from the `Series` class.
        """
        return QuerySuccessRatioSeries(
            name=name,
            metric="QUERY_SUCCESS_RATIO",
        )

    @classmethod
    def cron_count_metric(cls, name: str) -> "CronCountSeries":
        """Creates a Series of metric kind CronCount.

        Parameters
        ----------
        name
            A name for your new `cron_count` Series.

        Returns
        -------
        CronCountSeries
            A new `CronCountSeries` instance that inherits from the `Series` class.
        """
        return CronCountSeries(name=name, metric="CRON_COUNT", window_function="COUNT")

    @classmethod
    def cron_latency_metric(
        cls,
        name: str,
        window_function: Literal["count", "mean", "sum", "max", "99%", "95%", "75%", "50%", "25%", "5%", "min", "all"],
    ) -> "CronLatencySeries":
        """Creates a Series of metric kind `CronLatency`.

        Parameters
        ----------
        name
            A name for your new `cron_latency` Series.
        window_function
            The time window to calculate the metric over.

        Returns
        -------
        CronLatencySeries
            A new `CronLatencySeries` instance that inherits from the `Series` class.
        """
        if window_function not in {
            "count",
            "mean",
            "sum",
            "max",
            "99%",
            "95%",
            "75%",
            "50%",
            "25%",
            "5%",
            "min",
            "all",
        }:
            raise ValueError(f"window_function value '{window_function}' is not valid")
        return CronLatencySeries(name=name, metric="CRON_LATENCY", window_function=window_function)

    @classmethod
    def stream_message_latency_metric(
        cls,
        name: str,
        window_function: Literal["count", "mean", "sum", "max", "99%", "95%", "75%", "50%", "25%", "5%", "min", "all"],
    ) -> "StreamMessageLatencySeries":
        """Creates a Series of metric kind `StreamMessageLatency`.

        Parameters
        ----------
        name
            A name for your new `stream_message_latency` Series.
        window_function
            The time window to calculate the metric over.

        Returns
        -------
        StreamMessageLatencySeries
            A new `StreamMessageLatencySeries` instance that inherits from the `Series` class.
        """
        if window_function not in {
            "count",
            "mean",
            "sum",
            "max",
            "99%",
            "95%",
            "75%",
            "50%",
            "25%",
            "5%",
            "min",
            "all",
        }:
            raise ValueError(f"window_function value '{window_function}' is not valid")
        return StreamMessageLatencySeries(name=name, metric="STREAM_MESSAGE_LATENCY", window_function=window_function)

    @classmethod
    def stream_messages_processed_metric(
        cls,
        name: str,
        window_function: Literal["count", "mean", "sum", "max", "99%", "95%", "75%", "50%", "25%", "5%", "min", "all"],
    ) -> "StreamMessagesProcessedSeries":
        """Creates a Series of metric kind `StreamMessagesProcessed`.

        Parameters
        ----------
        name
            A name for your new `stream_messages_processed` Series.
        window_function
            The time window to calculate the metric over.

        Returns
        -------
        StreamMessagesProcessedSeries
            A new `StreamMessagesProcessedSeries` instance that inherits from the `Series` class.
        """
        if window_function not in {
            "count",
            "mean",
            "sum",
            "max",
            "99%",
            "95%",
            "75%",
            "50%",
            "25%",
            "5%",
            "min",
            "all",
        }:
            raise ValueError(f"window_function value '{window_function}' is not valid")
        return StreamMessagesProcessedSeries(
            name=name, metric="STREAM_MESSAGES_PROCESSED", window_function=window_function
        )

    @classmethod
    def stream_windows_processed_metric(
        cls,
        name: str,
        window_function: Literal["count", "mean", "sum", "max", "99%", "95%", "75%", "50%", "25%", "5%", "min", "all"],
    ) -> "StreamWindowsProcessedSeries":
        """Creates a Series of metric kind `StreamWindowsProcessed`.

        Parameters
        ----------
        name
            A name for your new `stream_windows_processed` Series.
        window_function
            The time window to calculate the metric over.

        Returns
        -------
        StreamWindowsProcessedSeries
            A new `StreamWindowsProcessedSeries` instance that inherits from the `Series` class.
        """
        if window_function not in {
            "count",
            "mean",
            "sum",
            "max",
            "99%",
            "95%",
            "75%",
            "50%",
            "25%",
            "5%",
            "min",
            "all",
        }:
            raise ValueError(f"window_function value '{window_function}' is not valid")
        return StreamWindowsProcessedSeries(
            name=name, metric="STREAM_WINDOWS_PROCESSED", window_function=window_function
        )

    @classmethod
    def stream_window_latency_metric(
        cls,
        name: str,
        window_function: Literal["count", "mean", "sum", "max", "99%", "95%", "75%", "50%", "25%", "5%", "min", "all"],
    ) -> "StreamWindowLatencySeries":
        """Creates a Series of metric kind `StreamWindowLatency`.

        Parameters
        ----------
        name
            A name for your new `stream_window_latency` Series.
        window_function
            The time window to calculate the metric over.

        Returns
        -------
        StreamWindowLatencySeries
            A new `StreamWindowLatencySeries` instance that inherits from the `Series` class.
        """
        if window_function not in {
            "count",
            "mean",
            "sum",
            "max",
            "99%",
            "95%",
            "75%",
            "50%",
            "25%",
            "5%",
            "min",
            "all",
        }:
            raise ValueError(f"window_function value '{window_function}' is not valid")
        return StreamWindowLatencySeries(name=name, metric="STREAM_WINDOW_LATENCY", window_function=window_function)


class FeatureRequestCountSeries(SeriesBase):
    """
    Series class for metric `feature_request_count`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        feature_tag: Optional[Union[List[str], str]] = None,
        feature: Optional[Union[List[Any], Any]] = None,
        is_null: Optional[bool] = None,
        feature_status: Optional[Literal["success", "failure"]] = None,
        cache_hit: Optional[bool] = None,
    ) -> "FeatureRequestCountSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        feature_tag:
            Filters for features matching the given tag(s).
        feature:
            Filters for values pertaining to the given feature.
        is_null:
            Filters for null values.
        feature_status:
            Filters for successes/failures of features.
        cache_hit:
            Filters for cache hits.

        Returns
        -------
        FeatureRequestCountSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            feature_tag=feature_tag,
            feature=feature,
            is_null=is_null,
            feature_status=feature_status,
            cache_hit=cache_hit,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        feature_tag: Optional[Union[List[str], str]] = None,
        feature: Optional[Union[List[Any], Any]] = None,
        is_null: Optional[bool] = None,
        feature_status: Optional[Literal["success", "failure"]] = None,
        cache_hit: Optional[bool] = None,
    ) -> "FeatureRequestCountSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        feature_tag:
            Filters for features matching the given tag(s).
        feature:
            Filters for values pertaining to the given feature.
        is_null:
            Filters for null values.
        feature_status:
            Filters for successes/failures of features.
        cache_hit:
            Filters for cache hits.

        Returns
        -------
        FeatureRequestCountSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            feature_tag=feature_tag,
            feature=feature,
            is_null=is_null,
            feature_status=feature_status,
            cache_hit=cache_hit,
            equals=False,
        )

    def group_by_resolver_type(self) -> "FeatureRequestCountSeries":
        """Attaches a `resolver_type` group-by to your Series instance.

        Returns
        -------
        FeatureRequestCountSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.ONLINE_OFFLINE)
        return copy

    def group_by_cache_hit(self) -> "FeatureRequestCountSeries":
        """Attaches a `cache_hit` group-by to your Series instance.

        Returns
        -------
        FeatureRequestCountSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.CACHE_HIT)
        return copy

    def group_by_is_null(self) -> "FeatureRequestCountSeries":
        """Attaches a `is_null` group-by to your Series instance.

        Returns
        -------
        FeatureRequestCountSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.IS_NULL)
        return copy

    def group_by_feature(self) -> "FeatureRequestCountSeries":
        """Attaches a `feature` group-by to your Series instance.

        Returns
        -------
        FeatureRequestCountSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.FEATURE_NAME)
        return copy


class FeatureStalenessSeries(SeriesBase):
    """
    Series class for metric `feature_staleness`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
    ) -> "FeatureStalenessSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.

        Returns
        -------
        FeatureStalenessSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
    ) -> "FeatureStalenessSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.

        Returns
        -------
        FeatureStalenessSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            equals=False,
        )

    def group_by_resolver_type(self) -> "FeatureStalenessSeries":
        """Attaches a `resolver_type` group-by to your Series instance.

        Returns
        -------
        FeatureStalenessSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.ONLINE_OFFLINE)
        return copy

    def group_by_cache_hit(self) -> "FeatureStalenessSeries":
        """Attaches a `cache_hit` group-by to your Series instance.

        Returns
        -------
        FeatureStalenessSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.CACHE_HIT)
        return copy


class FeatureValueSeries(SeriesBase):
    """
    Series class for metric `feature_value`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        feature_tag: Optional[Union[List[str], str]] = None,
        feature: Optional[Union[List[Any], Any]] = None,
        feature_status: Optional[Literal["success", "failure"]] = None,
        cache_hit: Optional[bool] = None,
    ) -> "FeatureValueSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        feature_tag:
            Filters for features matching the given tag(s).
        feature:
            Filters for values pertaining to the given feature.
        feature_status:
            Filters for successes/failures of features.
        cache_hit:
            Filters for cache hits.

        Returns
        -------
        FeatureValueSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            feature_tag=feature_tag,
            feature=feature,
            feature_status=feature_status,
            cache_hit=cache_hit,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        feature_tag: Optional[Union[List[str], str]] = None,
        feature: Optional[Union[List[Any], Any]] = None,
        feature_status: Optional[Literal["success", "failure"]] = None,
        cache_hit: Optional[bool] = None,
    ) -> "FeatureValueSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        feature_tag:
            Filters for features matching the given tag(s).
        feature:
            Filters for values pertaining to the given feature.
        feature_status:
            Filters for successes/failures of features.
        cache_hit:
            Filters for cache hits.

        Returns
        -------
        FeatureValueSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            feature_tag=feature_tag,
            feature=feature,
            feature_status=feature_status,
            cache_hit=cache_hit,
            equals=False,
        )

    def group_by_resolver_type(self) -> "FeatureValueSeries":
        """Attaches a `resolver_type` group-by to your Series instance.

        Returns
        -------
        FeatureValueSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.ONLINE_OFFLINE)
        return copy

    def group_by_cache_hit(self) -> "FeatureValueSeries":
        """Attaches a `cache_hit` group-by to your Series instance.

        Returns
        -------
        FeatureValueSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.CACHE_HIT)
        return copy

    def group_by_feature(self) -> "FeatureValueSeries":
        """Attaches a `feature` group-by to your Series instance.

        Returns
        -------
        FeatureValueSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.FEATURE_NAME)
        return copy


class FeatureNullRatioSeries(SeriesBase):
    """
    Series class for metric `feature_null_ratio`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        feature_tag: Optional[Union[List[str], str]] = None,
        feature: Optional[Union[List[Any], Any]] = None,
        feature_status: Optional[Literal["success", "failure"]] = None,
        cache_hit: Optional[bool] = None,
    ) -> "FeatureNullRatioSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        feature_tag:
            Filters for features matching the given tag(s).
        feature:
            Filters for values pertaining to the given feature.
        feature_status:
            Filters for successes/failures of features.
        cache_hit:
            Filters for cache hits.

        Returns
        -------
        FeatureNullRatioSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            feature_tag=feature_tag,
            feature=feature,
            feature_status=feature_status,
            cache_hit=cache_hit,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        feature_tag: Optional[Union[List[str], str]] = None,
        feature: Optional[Union[List[Any], Any]] = None,
        feature_status: Optional[Literal["success", "failure"]] = None,
        cache_hit: Optional[bool] = None,
    ) -> "FeatureNullRatioSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        feature_tag:
            Filters for features matching the given tag(s).
        feature:
            Filters for values pertaining to the given feature.
        feature_status:
            Filters for successes/failures of features.
        cache_hit:
            Filters for cache hits.

        Returns
        -------
        FeatureNullRatioSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            feature_tag=feature_tag,
            feature=feature,
            feature_status=feature_status,
            cache_hit=cache_hit,
            equals=False,
        )

    def group_by_resolver_type(self) -> "FeatureNullRatioSeries":
        """Attaches a `resolver_type` group-by to your Series instance.

        Returns
        -------
        FeatureNullRatioSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.ONLINE_OFFLINE)
        return copy

    def group_by_cache_hit(self) -> "FeatureNullRatioSeries":
        """Attaches a `cache_hit` group-by to your Series instance.

        Returns
        -------
        FeatureNullRatioSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.CACHE_HIT)
        return copy

    def group_by_feature(self) -> "FeatureNullRatioSeries":
        """Attaches a `feature` group-by to your Series instance.

        Returns
        -------
        FeatureNullRatioSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.FEATURE_NAME)
        return copy


class ResolverRequestCountSeries(SeriesBase):
    """
    Series class for metric `resolver_request_count`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "ResolverRequestCountSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        ResolverRequestCountSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "ResolverRequestCountSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        ResolverRequestCountSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=False,
        )

    def group_by_resolver_type(self) -> "ResolverRequestCountSeries":
        """Attaches a `resolver_type` group-by to your Series instance.

        Returns
        -------
        ResolverRequestCountSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.ONLINE_OFFLINE)
        return copy

    def group_by_cache_hit(self) -> "ResolverRequestCountSeries":
        """Attaches a `cache_hit` group-by to your Series instance.

        Returns
        -------
        ResolverRequestCountSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.CACHE_HIT)
        return copy

    def group_by_resolver(self) -> "ResolverRequestCountSeries":
        """Attaches a `resolver` group-by to your Series instance.

        Returns
        -------
        ResolverRequestCountSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.RESOLVER_NAME)
        return copy

    def group_by_resolver_status(self) -> "ResolverRequestCountSeries":
        """Attaches a `resolver_status` group-by to your Series instance.

        Returns
        -------
        ResolverRequestCountSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.RESOLVER_STATUS)
        return copy


class ResolverLatencySeries(SeriesBase):
    """
    Series class for metric `resolver_latency`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "ResolverLatencySeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        ResolverLatencySeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "ResolverLatencySeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        ResolverLatencySeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=False,
        )

    def group_by_resolver_type(self) -> "ResolverLatencySeries":
        """Attaches a `resolver_type` group-by to your Series instance.

        Returns
        -------
        ResolverLatencySeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.ONLINE_OFFLINE)
        return copy

    def group_by_cache_hit(self) -> "ResolverLatencySeries":
        """Attaches a `cache_hit` group-by to your Series instance.

        Returns
        -------
        ResolverLatencySeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.CACHE_HIT)
        return copy

    def group_by_resolver(self) -> "ResolverLatencySeries":
        """Attaches a `resolver` group-by to your Series instance.

        Returns
        -------
        ResolverLatencySeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.RESOLVER_NAME)
        return copy

    def group_by_resolver_status(self) -> "ResolverLatencySeries":
        """Attaches a `resolver_status` group-by to your Series instance.

        Returns
        -------
        ResolverLatencySeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.RESOLVER_STATUS)
        return copy


class ResolverSuccessRatioSeries(SeriesBase):
    """
    Series class for metric `resolver_success_ratio`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "ResolverSuccessRatioSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        ResolverSuccessRatioSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "ResolverSuccessRatioSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        ResolverSuccessRatioSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=False,
        )

    def group_by_resolver_type(self) -> "ResolverSuccessRatioSeries":
        """Attaches a `resolver_type` group-by to your Series instance.

        Returns
        -------
        ResolverSuccessRatioSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.ONLINE_OFFLINE)
        return copy

    def group_by_cache_hit(self) -> "ResolverSuccessRatioSeries":
        """Attaches a `cache_hit` group-by to your Series instance.

        Returns
        -------
        ResolverSuccessRatioSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.CACHE_HIT)
        return copy

    def group_by_resolver(self) -> "ResolverSuccessRatioSeries":
        """Attaches a `resolver` group-by to your Series instance.

        Returns
        -------
        ResolverSuccessRatioSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.RESOLVER_NAME)
        return copy

    def group_by_resolver_status(self) -> "ResolverSuccessRatioSeries":
        """Attaches a `resolver_status` group-by to your Series instance.

        Returns
        -------
        ResolverSuccessRatioSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.RESOLVER_STATUS)
        return copy


class QueryCountSeries(SeriesBase):
    """
    Series class for metric `query_count`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        query_name: Optional[Union[List[str], str]] = None,
        query_status: Optional[Literal["success", "failure"]] = None,
    ) -> "QueryCountSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        query_name:
            Filters for queries matching the given name(s).
        query_status:
            Filters for successes/failures of queries.

        Returns
        -------
        QueryCountSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            query_name=query_name,
            query_status=query_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        query_name: Optional[Union[List[str], str]] = None,
        query_status: Optional[Literal["success", "failure"]] = None,
    ) -> "QueryCountSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        query_name:
            Filters for queries matching the given name(s).
        query_status:
            Filters for successes/failures of queries.

        Returns
        -------
        QueryCountSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            query_name=query_name,
            query_status=query_status,
            equals=False,
        )

    def group_by_query_status(self) -> "QueryCountSeries":
        """Attaches a `query_status` group-by to your Series instance.

        Returns
        -------
        QueryCountSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.QUERY_STATUS)
        return copy

    def group_by_query_name(self) -> "QueryCountSeries":
        """Attaches a `query_name` group-by to your Series instance.

        Returns
        -------
        QueryCountSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.QUERY_NAME)
        return copy


class QueryLatencySeries(SeriesBase):
    """
    Series class for metric `query_latency`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        query_name: Optional[Union[List[str], str]] = None,
        query_status: Optional[Literal["success", "failure"]] = None,
    ) -> "QueryLatencySeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        query_name:
            Filters for queries matching the given name(s).
        query_status:
            Filters for successes/failures of queries.

        Returns
        -------
        QueryLatencySeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            query_name=query_name,
            query_status=query_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        query_name: Optional[Union[List[str], str]] = None,
        query_status: Optional[Literal["success", "failure"]] = None,
    ) -> "QueryLatencySeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        query_name:
            Filters for queries matching the given name(s).
        query_status:
            Filters for successes/failures of queries.

        Returns
        -------
        QueryLatencySeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            query_name=query_name,
            query_status=query_status,
            equals=False,
        )

    def group_by_query_status(self) -> "QueryLatencySeries":
        """Attaches a `query_status` group-by to your Series instance.

        Returns
        -------
        QueryLatencySeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.QUERY_STATUS)
        return copy

    def group_by_query_name(self) -> "QueryLatencySeries":
        """Attaches a `query_name` group-by to your Series instance.

        Returns
        -------
        QueryLatencySeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.QUERY_NAME)
        return copy


class QuerySuccessRatioSeries(SeriesBase):
    """
    Series class for metric `query_success_ratio`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        query_name: Optional[Union[List[str], str]] = None,
    ) -> "QuerySuccessRatioSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        query_name:
            Filters for queries matching the given name(s).

        Returns
        -------
        QuerySuccessRatioSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            query_name=query_name,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        query_name: Optional[Union[List[str], str]] = None,
    ) -> "QuerySuccessRatioSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        query_name:
            Filters for queries matching the given name(s).

        Returns
        -------
        QuerySuccessRatioSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            query_name=query_name,
            equals=False,
        )

    def group_by_query_name(self) -> "QuerySuccessRatioSeries":
        """Attaches a `query_name` group-by to your Series instance.

        Returns
        -------
        QuerySuccessRatioSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.QUERY_NAME)
        return copy


class CronCountSeries(SeriesBase):
    """
    Series class for metric `cron_count`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "CronCountSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        CronCountSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "CronCountSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        CronCountSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=False,
        )


class CronLatencySeries(SeriesBase):
    """
    Series class for metric `cron_latency`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "CronLatencySeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        CronLatencySeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_type: Optional[Union[List[ResolverType], ResolverType]] = None,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "CronLatencySeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_type:
            Filters for resolvers by type 'online', 'offline' or 'stream'.
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        CronLatencySeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_type=resolver_type,
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=False,
        )

    def group_by_resolver_type(self) -> "CronLatencySeries":
        """Attaches a `resolver_type` group-by to your Series instance.

        Returns
        -------
        CronLatencySeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.ONLINE_OFFLINE)
        return copy

    def group_by_cache_hit(self) -> "CronLatencySeries":
        """Attaches a `cache_hit` group-by to your Series instance.

        Returns
        -------
        CronLatencySeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.CACHE_HIT)
        return copy


class StreamMessageLatencySeries(SeriesBase):
    """
    Series class for metric `stream_message_latency`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "StreamMessageLatencySeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        StreamMessageLatencySeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "StreamMessageLatencySeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        StreamMessageLatencySeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=False,
        )

    def group_by_resolver_status(self) -> "StreamMessageLatencySeries":
        """Attaches a `resolver_status` group-by to your Series instance.

        Returns
        -------
        StreamMessageLatencySeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.RESOLVER_STATUS)
        return copy


class StreamMessagesProcessedSeries(SeriesBase):
    """
    Series class for metric `stream_messages_processed`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "StreamMessagesProcessedSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        StreamMessagesProcessedSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "StreamMessagesProcessedSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        StreamMessagesProcessedSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=False,
        )

    def group_by_resolver_status(self) -> "StreamMessagesProcessedSeries":
        """Attaches a `resolver_status` group-by to your Series instance.

        Returns
        -------
        StreamMessagesProcessedSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.RESOLVER_STATUS)
        return copy


class StreamWindowsProcessedSeries(SeriesBase):
    """
    Series class for metric `stream_windows_processed`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "StreamWindowsProcessedSeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        StreamWindowsProcessedSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "StreamWindowsProcessedSeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        StreamWindowsProcessedSeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=False,
        )

    def group_by_resolver_status(self) -> "StreamWindowsProcessedSeries":
        """Attaches a `resolver_status` group-by to your Series instance.

        Returns
        -------
        StreamWindowsProcessedSeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.RESOLVER_STATUS)
        return copy


class StreamWindowLatencySeries(SeriesBase):
    """
    Series class for metric `stream_window_latency`
    """

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def where(
        self,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "StreamWindowLatencySeries":
        """Attaches a filter to your Series instance.

        Parameters
        ----------
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        StreamWindowLatencySeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=True,
        )

    def where_not(
        self,
        resolver_tag: Optional[Union[List[str], str]] = None,
        resolver: Optional[Union[List[Union[ResolverProtocol, str]], Union[ResolverProtocol, str]]] = None,
        resolver_status: Optional[Literal["success", "failure"]] = None,
    ) -> "StreamWindowLatencySeries":
        """Attaches a negative filter to your Series instance.

        Parameters
        ----------
        resolver_tag:
            Filters for resolvers matching the given tag(s).
        resolver:
            Filters for values pertaining to the given resolver.
        resolver_status:
            Filters for successes/failures of resolvers.

        Returns
        -------
        StreamWindowLatencySeries
            A copy of your series with the new filter
        """
        return self._where(
            resolver_tag=resolver_tag,
            resolver=resolver,
            resolver_status=resolver_status,
            equals=False,
        )

    def group_by_resolver_status(self) -> "StreamWindowLatencySeries":
        """Attaches a `resolver_status` group-by to your Series instance.

        Returns
        -------
        StreamWindowLatencySeries
            A copy of your series with the new group-by
        """
        copy = self._copy_with()
        copy._group_by.append(GroupByKind.RESOLVER_STATUS)
        return copy
