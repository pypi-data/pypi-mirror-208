import sys
from typing import Any, Callable, Dict, List, Optional, Type, Union

from pydantic import Field, StrictBool, StrictStr

from unfolded.map_sdk.api.base import (
    Action,
    CamelCaseBaseModel,
    Number,
    Range,
    TimeRange,
)
from unfolded.map_sdk.api.enums import ActionType, FilterType
from unfolded.map_sdk.transport.base import (
    BaseInteractiveTransport,
    BaseNonInteractiveTransport,
    BaseTransport,
)
from unfolded.map_sdk.utils.validators import validate_kwargs

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class _PartialFilterSource(CamelCaseBaseModel):
    """Partially defined filter source where the datasetId can be left out."""

    data_id: Optional[StrictStr]
    """Identifier of the dataset that the filter applies to."""

    field_name: StrictStr
    """Field name to filter by.
    The field name can be retrieved as part of the dataset record.
    """


class FilterSource(_PartialFilterSource):
    """Source that the filter is applied to."""

    data_id: StrictStr
    """Identifier of the dataset that the filter applies to."""

    field_name: StrictStr
    """Field name to filter by. The field name can be retrieved as part of the dataset record.
    """


class _PartialBaseFilter(CamelCaseBaseModel):
    """Partial version of Filter for Filter creation"""

    id: Optional[StrictStr]
    """Unique identifier of the filter."""

    type: FilterType
    """Type of the filter."""

    # Incompatible types in assignment (expression has type "List[_T]", variable has type
    # "List[_PartialFilterSource]")  [assignment]
    sources: List[_PartialFilterSource] = Field(default_factory=list)
    """ Data source(s) to apply the filter to.
    note: Only TimeRangeFilter currently supports multiple sources.
    The first given source will be used for other filter types.
    """

    value: Any
    """Value to filter based on."""


class BaseFilter(_PartialBaseFilter):
    """Type encapsulating common filter properties."""

    id: StrictStr
    # Incompatible types in assignment (expression has type "List[FilterSource]", base class
    # "_PartialBaseFilter" defined the type as "List[_PartialFilterSource]")
    sources: List[FilterSource]  # type: ignore[assignment]


class _PartialRangeFilter(_PartialBaseFilter):
    """Partial RangeFilter for Filter creation"""

    type = FilterType.RANGE
    value: Range


class RangeFilter(BaseFilter):
    """Filter type that filters a range of values."""

    type = FilterType.RANGE
    value: Range


class _PartialSelectFilter(_PartialBaseFilter):
    """Partial SelectFilter for Filter creation"""

    type = FilterType.SELECT
    value: StrictBool


class SelectFilter(BaseFilter):
    """Filter type that filters a range of values."""

    type = FilterType.SELECT
    value: StrictBool


FilterView = Literal["side", "enlarged", "minified"]


class FilterTimelineUpdateProps(CamelCaseBaseModel):
    """A set of properties that can be updated on a timeline."""

    view: Optional[FilterView]
    """Current timeline presentation."""

    time_format: Optional[StrictStr]
    """Time format that the timeline is using in day.js supported format.
    https://day.js.org/docs/en/display/format
    """

    timezone: Optional[StrictStr]
    """Timezone that the timeline is using in tz format.
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """

    is_animating: Optional[StrictBool]
    """Flag indicating whether the timeline is animating or not."""

    animation_speed: Optional[Number]
    """Speed at which timeline is animating."""


class FilterTimeline(FilterTimelineUpdateProps):
    """Time range filter properties that encapsulate timeline interaction."""

    view: FilterView
    """Current timeline presentation."""

    time_format: StrictStr
    """Time format that the timeline is using in day.js supported format.
    https://day.js.org/docs/en/display/format
    """

    timezone: Optional[StrictStr]
    """Timezone that the timeline is using in tz format.
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """

    is_animating: StrictBool
    """Flag indicating whether the timeline is animating or not."""

    animation_speed: Number
    """Speed at which timeline is animating."""

    step: Number
    """Minimum animation step size in milliseconds."""


class _PartialTimeRangeFilter(_PartialBaseFilter):
    """Partial TimeRangeFilter for Filter creation"""

    type = FilterType.TIME_RANGE
    value: TimeRange
    domain: TimeRange
    timeline: FilterTimeline


class TimeRangeFilter(BaseFilter):

    type = FilterType.TIME_RANGE
    value: TimeRange
    domain: TimeRange
    timeline: FilterTimeline


class _PartialMultiSelectFilter(_PartialBaseFilter):
    """Partial MultiSelectFilter for Filter creation"""

    type = FilterType.MULTI_SELECT
    value: List[StrictStr]


class MultiSelectFilter(BaseFilter):
    """Filter type that filters a range of values."""

    type = FilterType.MULTI_SELECT
    value: List[StrictStr]


# Note that using a union like this as a pydantic type means that pydantic will try to match the
# input against each model in turn. This means that with this approach, we can't have any
# overlapping models definitinos, because there would be no way to know which filter is actually
# desired. Or we need to put the narrowest field first in the list.
#
# If that doesn't work, we would need to add a discriminator field like type
_PartialFilter = Union[
    _PartialRangeFilter,
    _PartialSelectFilter,
    _PartialTimeRangeFilter,
    _PartialMultiSelectFilter,
]
FilterCreationProps = _PartialFilter
FilterUpdateProps = _PartialFilter

PARTIAL_FILTER_CLASSES: Dict[FilterType, Type[_PartialFilter]] = {
    FilterType.RANGE: _PartialRangeFilter,
    FilterType.SELECT: _PartialSelectFilter,
    FilterType.TIME_RANGE: _PartialTimeRangeFilter,
    FilterType.MULTI_SELECT: _PartialMultiSelectFilter,
}


Filter = Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]


class _FilterTimelineUpdateProps(CamelCaseBaseModel):

    view: Optional[FilterView]
    """Current timeline presentation."""

    time_format: Optional[StrictStr]
    """Time format that the timeline is using in day.js supported format.
    https://day.js.org/docs/en/display/format
    """

    timezone: Optional[StrictStr]
    """Timezone that the timeline is using in tz format.
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """

    is_animating: Optional[StrictBool]
    """Flag indicating whether the timeline is animating or not."""

    animation_speed: Optional[Number]
    """Speed at which timeline is animating."""


class FilterEventHandlers(CamelCaseBaseModel):
    on_filter_update: Optional[Callable[[Filter], None]]


###########
# ACTIONS #
###########


class GetFiltersAction(Action):
    """Action payload sent with `get_filters` calls"""

    type = ActionType.GET_FILTERS


class GetFilterByIdAction(Action):
    """Action payload sent with `get_filter_by_id` calls"""

    class Meta(Action.Meta):
        args = ["filter_id"]

    type = ActionType.GET_FILTER_BY_ID
    filter_id: StrictStr


class AddFilterAction(Action):
    class Meta(Action.Meta):
        args = ["filter"]

    type = ActionType.ADD_FILTER
    filter: FilterCreationProps


class UpdateFilterAction(Action):
    class Meta(Action.Meta):
        args = ["filter_id", "values"]

    type = ActionType.UPDATE_FILTER
    filter_id: StrictStr
    values: FilterUpdateProps


class RemoveFilterAction(Action):
    class Meta(Action.Meta):
        args = ["filter_id"]

    type = ActionType.REMOVE_FILTER
    filter_id: StrictStr


class UpdateTimelineAction(Action):
    class Meta(Action.Meta):
        args = ["filter_id", "values"]

    type = ActionType.UPDATE_TIMELINE
    filter_id: StrictStr
    values: _FilterTimelineUpdateProps


###########
# METHODS #
###########


class BaseFilterApiMethods:

    transport: BaseTransport

    @validate_kwargs(positional_only=["filter"])
    def add_filter(
        self,
        # pylint:disable = redefined-builtin
        filter: Union[FilterCreationProps, dict, None] = None,
        **kwargs: Any,
    ) -> Optional[Filter]:
        """Adds a new filter to the map.

        Args:
            filter (FilterCreationProps): The filter to add.

        Returns (widget map only):
            Filter: The filter that was added.
        """
        action = AddFilterAction(filter=filter if filter is not None else kwargs)

        # Fails mypy because Filter is a Union
        return self.transport.send_action_non_null(action=action, response_class=Filter)  # type: ignore[arg-type]

    @validate_kwargs(positional_only=["filter_id", "values"])
    def update_filter(
        self,
        filter_id: str,
        values: Union[FilterUpdateProps, dict, None] = None,
        **kwargs: Any,
    ) -> Optional[Filter]:
        """Updates an existing filter with given values.

        Args:
            filter_id (str): The id of the filter to update.
            values (Union[FilterUpdateProps, dict, None], optional): The new filter values. Defaults to None.

        Returns (widget map only):
            Filter: The updated filter.
        """
        action = UpdateFilterAction(
            filter_id=filter_id, values=values if values is not None else kwargs
        )

        # Fails mypy because Filter is a Union
        return self.transport.send_action_non_null(action=action, response_class=Filter)  # type: ignore[arg-type]

    @validate_kwargs(positional_only=["filter_id"])
    def remove_filter(self, filter_id: str) -> None:
        """Removes a filter from the map.

        Args:
            filter_id (str): The id of the filter to remove.

        Returns:
            None
        """
        action = RemoveFilterAction(filter_id=filter_id)
        self.transport.send_action(action=action, response_class=None)

    @validate_kwargs(positional_only=["filter_id", "values"])
    def update_timeline(
        self,
        filter_id: str,
        values: Union[FilterTimelineUpdateProps, dict, None] = None,
        **kwargs: Any,
    ) -> Optional[TimeRangeFilter]:
        """Updates a time range filter timeline with given values.

        Args:
            filter_id (str): The id of the time range filter to update.
            values (Union[FilterTimelineUpdateProps, dict, None], optional): The new timeline values. Defaults to None.

        Returns (widget map only):
            TimeRangeFilter: The updated time range filter.
        """
        action = UpdateTimelineAction(
            filter_id=filter_id, values=values if values is not None else kwargs
        )

        return self.transport.send_action_non_null(
            action=action, response_class=TimeRangeFilter
        )


class BaseInteractiveFilterApiMethods:

    transport: BaseInteractiveTransport

    def get_filters(self) -> List[Filter]:
        """Gets all the filters currently available in the map.

        Returns:
            List[Filter]: An array of filters.
        """
        action = GetFiltersAction()
        return self.transport.send_action_non_null(
            action=action, response_class=List[Filter]
        )

    @validate_kwargs(positional_only=["filter_id"])
    def get_filter_by_id(self, filter_id: str) -> Optional[Filter]:
        """Retrieves a filter by its identifier if it exists.

        Args:
            filter_id (str): Identifier of the filter to get.

        Returns:
            Optional[Filter]: Filter with a given identifier, or None if one doesn't exist.
        """
        action = GetFilterByIdAction(filter_id=filter_id)

        # Fails mypy because Filter is a Union
        return self.transport.send_action(action=action, response_class=Filter)  # type: ignore[arg-type]


class FilterApiNonInteractiveMixin(BaseFilterApiMethods):
    """Filter methods that are supported in non-interactive (i.e. pure HTML) maps"""

    transport: BaseNonInteractiveTransport

    def add_filter(
        self,
        # pylint:disable = redefined-builtin
        filter: Union[FilterCreationProps, dict, None] = None,
        **kwargs: Any,
    ) -> None:
        super().add_filter(filter, **kwargs)
        return

    @validate_kwargs(positional_only=["filter_id", "values"])
    def update_filter(
        self,
        filter_id: str,
        values: Union[FilterUpdateProps, dict, None] = None,
        **kwargs: Any,
    ) -> None:
        super().update_filter(filter_id, values, **kwargs)
        return

    @validate_kwargs(positional_only=["filter_id", "values"])
    def update_timeline(
        self,
        filter_id: str,
        values: Union[FilterTimelineUpdateProps, dict, None] = None,
        **kwargs: Any,
    ) -> None:
        super().update_timeline(filter_id, values, **kwargs)
        return


class FilterApiInteractiveMixin(BaseFilterApiMethods, BaseInteractiveFilterApiMethods):

    transport: BaseInteractiveTransport

    def add_filter(
        self,
        # pylint:disable = redefined-builtin
        filter: Union[FilterCreationProps, dict, None] = None,
        **kwargs: Any,
    ) -> Filter:
        return super().add_filter(filter, **kwargs)

    @validate_kwargs(positional_only=["filter_id", "values"])
    def update_filter(
        self,
        filter_id: str,
        values: Union[FilterUpdateProps, dict, None] = None,
        **kwargs: Any,
    ) -> Filter:
        return super().update_filter(filter_id, values, **kwargs)

    @validate_kwargs(positional_only=["filter_id", "values"])
    def update_timeline(
        self,
        filter_id: str,
        values: Union[FilterTimelineUpdateProps, dict, None] = None,
        **kwargs: Any,
    ) -> TimeRangeFilter:
        return super().update_timeline(filter_id, values, **kwargs)
