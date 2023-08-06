import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, overload

from geojson_pydantic import Feature, Polygon
from pydantic import AnyHttpUrl, StrictBool, StrictInt, StrictStr

from unfolded.map_sdk.api.base import (
    Action,
    CamelCaseBaseModel,
    KebabCaseBaseModel,
    Number,
)
from unfolded.map_sdk.api.dataset_api import _DatasetCreationProps
from unfolded.map_sdk.api.enums import ActionType
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


class _PartialView(CamelCaseBaseModel):
    """Partial version of View for data input type"""

    longitude: Optional[Number]
    """Longitude of the view center [-180, 180]."""

    latitude: Optional[Number]
    """Latitude of the view center [-90, 90]."""

    zoom: Optional[Number]
    """View zoom level [0-22]."""

    pitch: Optional[Number]
    """View pitch value [0-90]."""

    bearing: Optional[Number]
    """View bearing [0-360]."""


class View(_PartialView):
    """Strict version of _PartialView for method return type"""

    longitude: Number
    """Longitude of the view center [-180, 180]."""

    latitude: Number
    """Latitude of the view center [-90, 90]."""

    zoom: Number
    """View zoom level [0-22]."""

    pitch: Number
    """View pitch value [0-90]."""

    bearing: Number
    """View bearing [0-360]."""


class Bounds(CamelCaseBaseModel):
    min_longitude: Number
    """The west bound."""

    max_longitude: Number
    """The east bound."""

    min_latitude: Number
    """The south bound."""

    max_latitude: Number
    """The north bound."""


class _PartialViewLimits(CamelCaseBaseModel):
    """Partial version of ViewLimits for data input type"""

    min_zoom: Optional[Number]
    """Minimum zoom of the map [0-22]"""

    max_zoom: Optional[Number]
    """Maximum zoom of the map [0-22]"""

    max_bounds: Optional[Bounds]
    """Maximum bounds of the map."""


class ViewLimits(_PartialViewLimits):
    """Strict version of _PartialViewLimits for method return type"""

    min_zoom: Number
    """Minimum zoom of the map [0-22]"""

    max_zoom: Number
    """Maximum zoom of the map [0-22]"""

    max_bounds: Bounds
    """Maximum bounds of the map."""


class _PartialMapControlVisibility(KebabCaseBaseModel):
    """Partial version of View for data input type"""

    legend: Optional[StrictBool]
    """Whether the legend is visible."""

    toggle_3d: Optional[StrictBool]
    """Whether the 3D toggle is visible."""

    split_map: Optional[StrictBool]
    """Whether the split map button is visible."""

    map_draw: Optional[StrictBool]
    """Whether the map draw button is visible."""


class MapControlVisibility(_PartialMapControlVisibility):
    """Strict version of _PartialMapControlVisibility for method return type"""

    legend: StrictBool
    """Whether the legend is visible."""

    toggle_3d: StrictBool
    """Whether the 3D toggle is visible."""

    split_map: StrictBool
    """Whether the split map button is visible."""

    map_draw: StrictBool
    """Whether the map draw button is visible."""


SplitMode = Literal["single", "dual", "swipe"]


class _PartialSplitModeContext(CamelCaseBaseModel):
    layers: Optional[List[List[StrictStr]]]
    """An array of layer ids to show on either side of the split. Only applicable for multi-view split modes."""

    is_view_synced: Optional[StrictBool]
    """Boolean indicating whether views are synced. Only applicable to dual split mode."""

    is_zoom_synced: Optional[StrictBool]
    """Boolean indicating whether zoom is synced between views. Only applicable to dual split mode."""


class SplitModeContext(_PartialSplitModeContext):
    """Base type that contains context around the split map mode."""

    layers: List[List[StrictStr]]
    """An array of layer ids to show on either side of the split. Only applicable for multi-view split modes."""

    is_view_synced: StrictBool
    """Boolean indicating whether views are synced. Only applicable to dual split mode."""

    is_zoom_synced: StrictBool
    """Boolean indicating whether zoom is synced between views. Only applicable to dual split mode."""


class SplitModeDetails(SplitModeContext):
    """Container type for split map mode details."""

    split_mode: SplitMode


SetSplitModeOptions = _PartialSplitModeContext

ThemePresets = Literal["light", "dark"]


class ThemeOptions(CamelCaseBaseModel):

    background_color: Optional[StrictStr]
    """Background color of UI elements"""


class ThemeUpdateProps(CamelCaseBaseModel):

    preset: Optional[ThemePresets]
    """Preset UI theme name"""

    options: Optional[ThemeOptions]
    """UI theme update options"""


class MapStyleLayerGroup(CamelCaseBaseModel):
    """A grouping concept for basemap layers, allowing for interaction on a set of layers."""

    label: StrictStr
    """Layer group text representation.
    The currently supported labels are: label, road, border, building, water, land, 3d building.
    """

    default_visibility: StrictBool
    """Whether map style this group should be visible by default."""


class MapStyleLayerGroupCreationProps(MapStyleLayerGroup):
    """A set of properties required when specifying a map style layer group."""

    filter: StrictStr
    """
    Layer filtering regular expression that determines whether layer with a given id should be part of this group.

    Supports regular JS RegExp syntax (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp).
    """


class MapStyleCreationProps(CamelCaseBaseModel):
    """A set of properties required when specifying a map style."""

    id: Optional[StrictStr]
    """Unique identifier of the map style."""

    thumbnail_url: Optional[StrictStr]
    """URL of the thumbnail to show alongside the map style."""

    layer_groups: Optional[List[MapStyleLayerGroupCreationProps]]
    """An array of map style layer groups."""


class MapStyle(MapStyleCreationProps):
    """
    Style applied to the underlying map style. The map style descriptor must conform
    to the Mapbox style specification (https://docs.mapbox.com/mapbox-gl-js/style-spec/).
    """

    id: StrictStr
    """Unique identifier of the map style."""

    label: StrictStr
    """User facing map style label."""

    url: AnyHttpUrl
    """URL of the map style descriptor json in Mapbox style format."""

    thumbnail_url: StrictStr
    """URL of the thumbnail to show alongside the map style."""

    layer_groups: List[MapStyleLayerGroup]  # type:ignore[assignment]
    """An array of map style layer groups."""


class SetMapConfigOptions(CamelCaseBaseModel):

    additional_datasets: Optional[List[_DatasetCreationProps]]
    """Datasets to add to the map before loading the map configuration."""


class PickInfo(CamelCaseBaseModel):
    """Additional context on map data associated to this event."""

    layer_id: StrictStr
    """Identifier of the layer that the mouse event is related to."""

    row_index: Number
    """Index of the row in the data table that picked layer visualizes."""

    row_data: List[Any]
    """Row data that the picked layer visualizes."""


class MouseEvent(CamelCaseBaseModel):
    """Mouse event capturing information such as position and any map features related to it."""

    coordinate: Tuple[Number, Number]
    """Geospatial coordinates [longitude, latitude]."""

    position: Tuple[Number, Number]
    """Mouse position relative to the viewport [x, y]."""

    pick_info: Optional[PickInfo]
    """Additional context on map data associated to this event."""


class GeometrySelectionEvent(CamelCaseBaseModel):
    features: List[Feature[Polygon, Any]]


OnHoverHandlerType = Callable[[MouseEvent], None]
OnClickHandlerType = Callable[[MouseEvent], None]
OnViewUpdateType = Callable[[View], None]
OnGeometrySelectionType = Callable[[GeometrySelectionEvent], None]


class MapEventHandlers(CamelCaseBaseModel):
    """Event handlers which can be registered for receiving notifications of certain map events."""

    on_click: Optional[OnClickHandlerType]
    """Called whenever user clicks the visible part of the map."""

    on_hover: Optional[OnHoverHandlerType]
    """Called whenever a mouse hovers over a visible part of the map."""

    on_view_update: Optional[OnViewUpdateType]
    """Called whenever visible map viewport changes."""

    on_geometry_selection: Optional[OnGeometrySelectionType]
    """Called whenever a geometry is drawn in the map."""


###########
# ACTIONS #
###########


class GetViewAction(Action):
    """Action payload sent with `get_view` calls"""

    class Meta(Action.Meta):
        args = ["index"]

    type: ActionType = ActionType.GET_VIEW
    index: StrictInt


class SetViewAction(Action):
    """Action payload sent with `set_view` calls"""

    class Meta(Action.Meta):
        args = ["view"]
        options = ["index"]

    type: ActionType = ActionType.SET_VIEW
    view: _PartialView
    index: StrictInt
    """Index of the view to update, relevant when multi-view split mode is used and views are unlocked."""


class GetViewLimitsAction(Action):
    """Action payload sent with `get_view_limits` calls"""

    class Meta(Action.Meta):
        args = ["index"]

    type: ActionType = ActionType.GET_VIEW_LIMITS
    index: StrictInt


class SetViewLimitsAction(Action):
    """Action payload sent with `set_view_limits` calls"""

    class Meta(Action.Meta):
        args = ["view_limits"]
        options = ["index"]

    type: ActionType = ActionType.SET_VIEW_LIMITS
    view_limits: _PartialViewLimits
    index: StrictInt
    """Index of the view limits to update, relevant when multi-view split mode is used and views are unlocked."""


class GetMapControlVisibilityAction(Action):
    """Action payload sent with `get_map_control_visibility` calls"""

    type: ActionType = ActionType.GET_MAP_CONTROL_VISIBILITY


class SetMapControlVisibilityAction(Action):
    """Action payload sent with `set_map_control_visibility` calls"""

    class Meta(Action.Meta):
        args = ["visibility"]

    type: ActionType = ActionType.SET_MAP_CONTROL_VISIBILITY
    visibility: _PartialMapControlVisibility


class GetSplitModeAction(Action):
    """Action payload sent with `get_split_mode` calls"""

    type: ActionType = ActionType.GET_SPLIT_MODE


class SetSplitModeAction(Action):
    """Action payload sent with `set_split_mode` calls"""

    class Meta(Action.Meta):
        args = ["split_mode", "options"]

    type: ActionType = ActionType.SET_SPLIT_MODE
    split_mode: SplitMode
    options: SetSplitModeOptions


class SetThemeAction(Action):
    """Action payload sent with `set_theme`calls"""

    class Meta(Action.Meta):
        args = ["theme"]

    type: ActionType = ActionType.SET_THEME
    theme: ThemeUpdateProps


class GetMapStylesAction(Action):

    type: ActionType = ActionType.GET_MAP_STYLES


class GetMapConfigAction(Action):

    type: ActionType = ActionType.GET_MAP_CONFIG


class SetMapConfigAction(Action):
    class Meta(Action.Meta):
        args = ["config", "options"]

    type: ActionType = ActionType.SET_MAP_CONFIG

    config: Dict[StrictStr, Any]
    options: Optional[SetMapConfigOptions]


###########
# METHODS #
###########


class BaseMapApiMethods:

    transport: BaseTransport

    @validate_kwargs(positional_only=["view"])
    def set_view(
        self, view: Union[View, dict, None] = None, index: int = 0, **kwargs: Number
    ) -> Optional[View]:
        """Sets a new view state for the map.

        Args:
            view: View model instance or a dict with the same attributes, all optional.

        Kwargs (cannot be used with positional arg):
            latitude: Longitude of the view center [-180, 180].
            longitude: Latitude of the view center [-90, 90].
            zoom: View zoom level [0-22].
            pitch: View pitch value [0-90].
            bearing: View bearing [0-360].

        Returns (widget map only):
            View: The new view state of the map.
        """
        action = SetViewAction(view=view if view is not None else kwargs, index=index)
        return self.transport.send_action_non_null(action=action, response_class=View)

    @validate_kwargs(positional_only=["view_limits"])
    def set_view_limits(
        self,
        view_limits: Union[ViewLimits, dict, None] = None,
        index: int = 0,
        **kwargs: Union[Number, Bounds, dict],
    ) -> Optional[ViewLimits]:
        """Sets new view limits for the map.

        Args:
            view_limits: ViewLimits model instance or a dict with the same attributes, all optional.

        Kwargs (cannot be used with positional arg):
            min_zoom: Minimum zoom of the map [0-22].
            max_zoom: Maximum zoom of the map [0-22].
            max_bounds: a Bounds object or a dict with the keys (`min_longitude`, `max_longitude`, `min_latitude`, `max_latitude`).

        Returns (widget map only):
            ViewLimits: The new view limits of the map.
        """
        action = SetViewLimitsAction(
            view_limits=view_limits if view_limits is not None else kwargs, index=index
        )
        return self.transport.send_action_non_null(
            action=action, response_class=ViewLimits
        )

    @validate_kwargs(positional_only=["visibility"])
    def set_map_control_visibility(
        self, visibility: Union[MapControlVisibility, dict, None] = None, **kwargs: bool
    ) -> Optional[MapControlVisibility]:
        """Sets new map control visibility for the map.

        Args:
            visibility: MapControlVisibility model instance or a dict with the same attributes, all optional.

        Kwargs (cannot be used with positional arg):
            legend: Whether the legend is visible.
            toggle_3d: Whether the 3D toggle is visible.
            split_map: Whether the split map button is visible.
            map_draw: Whether the map draw button is visible.

        Returns (widget map only):
            MapControlVisibility: The new map control visibility of the map.
        """
        action = SetMapControlVisibilityAction(
            visibility=visibility if visibility is not None else kwargs
        )
        return self.transport.send_action_non_null(
            action=action, response_class=MapControlVisibility
        )

    @validate_kwargs(positional_only=["split_mode", "options"])
    def set_split_mode(
        self,
        split_mode: SplitMode,
        options: Union[SplitModeContext, dict, None] = None,
        **kwargs: Any,
    ) -> Optional[SplitModeDetails]:
        """Sets a new split mode for the map.

        Args:
            split_mode: The desired split mode.
            options: SplitModeContext model instance or a dict with the same attributes.

        Kwargs (cannot be used with positional arg):
            layers: Arrays with layer Ids per each post-split map section.

        Returns (widget map only):
            SplitModeDetails: The new split mode of the map.
        """
        action = SetSplitModeAction(
            split_mode=split_mode, options=options if options is not None else kwargs
        )
        return self.transport.send_action_non_null(
            action=action, response_class=SplitModeDetails
        )

    def set_theme(
        self,
        *,
        preset: Optional[ThemePresets] = None,
        background_color: Optional[str] = None,
    ) -> None:
        """Sets a UI theme for the map

        Kwargs:
            preset: a preset theme: "light" or "dark"
            background_color: background color of UI elements

        Returns:
            None
        """
        props = ThemeUpdateProps(
            preset=preset, options={"background_color": background_color}
        )
        action = SetThemeAction(theme=props)
        return self.transport.send_action(action=action, response_class=None)

    @validate_kwargs(positional_only=["config", "options"])
    def set_map_config(
        self,
        config: dict,
        options: Union[dict, SetMapConfigOptions, None] = None,
        **kwargs,
    ) -> None:
        """Loads the given configuration into the current map.

        Args:
            config (dict): Configuration to load into the map. For details around the format see https://location.foursquare.com/developer/docs/studio-map-configuration.
            options (Optional[SetMapConfigOptions]): A set of options for the map configuration.

        Kwargs (cannot be used with positional arg):
            additional_datasets: Datasets to add to the map before loading the map configuration.

        Returns:
            None
        """
        action = SetMapConfigAction(
            config=config, options=options if options else kwargs
        )
        return self.transport.send_action(action=action, response_class=None)


class BaseInteractiveMapApiMethods:

    transport: BaseInteractiveTransport

    @overload
    def get_view(self, index: Literal[0] = 0) -> View:
        ...

    @overload
    def get_view(self, index: int = 0) -> Optional[View]:
        ...

    def get_view(self, index: int = 0) -> Optional[View]:
        """Gets the current view state of the map.

        Returns:
            The current view state of the map.
        """
        action = GetViewAction(index=index)
        return self.transport.send_action(action=action, response_class=View)

    @overload
    def get_view_limits(self, index: Literal[0] = 0) -> ViewLimits:
        ...

    @overload
    def get_view_limits(self, index: int = 0) -> Optional[ViewLimits]:
        ...

    def get_view_limits(self, index: int = 0) -> Optional[ViewLimits]:
        """Gets the current view limits of the map.

        Returns:
            The current view limits of the map.
        """
        action = GetViewLimitsAction(index=index)
        return self.transport.send_action(action=action, response_class=ViewLimits)

    def get_map_styles(self) -> List[MapStyle]:
        """Gets the currently available map styles.

        Returns:
            List[MapStyle]: All currently available map styles.
        """
        action = GetMapStylesAction()
        return self.transport.send_action_non_null(
            action=action, response_class=List[MapStyle]
        )

    def get_map_control_visibility(self) -> MapControlVisibility:
        """Gets the current map control visibility of the map.

        Returns:
            The current map control visibility of the map.
        """
        action = GetMapControlVisibilityAction()
        return self.transport.send_action_non_null(
            action=action, response_class=MapControlVisibility
        )

    def get_split_mode(self) -> SplitModeContext:
        """Gets the current split mode of the map.

        Returns:
            The current split mode of the map.
        """
        action = GetSplitModeAction()
        return self.transport.send_action_non_null(
            action=action, response_class=SplitModeContext
        )

    def get_map_config(self) -> dict:
        """Gets the configuration representing the current map state.

        Returns:
            dict: Current map configuration. For details around the format see @link https://location.foursquare.com/developer/docs/studio-map-configuration.
        """
        action = GetMapConfigAction()
        return self.transport.send_action_non_null(action=action, response_class=dict)


class MapApiNonInteractiveMixin(BaseMapApiMethods):
    """Map methods that are supported in non-interactive (i.e. pure HTML) maps"""

    transport: BaseNonInteractiveTransport

    def set_view(
        self, view: Union[View, dict, None] = None, index: int = 0, **kwargs: Number
    ) -> None:
        super().set_view(view, index=index, **kwargs)
        return

    def set_view_limits(
        self,
        view_limits: Union[ViewLimits, dict, None] = None,
        index: int = 0,
        **kwargs: Union[Number, Bounds, dict],
    ) -> None:
        super().set_view_limits(view_limits, index=index, **kwargs)
        return

    def set_map_control_visibility(
        self, visibility: Union[MapControlVisibility, dict, None] = None, **kwargs: bool
    ) -> None:
        super().set_map_control_visibility(visibility, **kwargs)
        return

    def set_split_mode(
        self,
        split_mode: SplitMode,
        options: Union[SplitModeContext, dict, None] = None,
        **kwargs: Any,
    ) -> None:
        super().set_split_mode(split_mode, options, **kwargs)
        return


class MapApiInteractiveMixin(BaseMapApiMethods, BaseInteractiveMapApiMethods):
    """Map methods that are supported in interactive (i.e. widget) maps"""

    transport: BaseInteractiveTransport

    def set_view(
        self, view: Union[View, dict, None] = None, index: int = 0, **kwargs: Number
    ) -> View:
        return super().set_view(view, index=index, **kwargs)

    def set_view_limits(
        self,
        view_limits: Union[ViewLimits, dict, None] = None,
        index: int = 0,
        **kwargs: Union[Number, Bounds, dict],
    ) -> ViewLimits:
        return super().set_view_limits(view_limits, index=index, **kwargs)

    def set_map_control_visibility(
        self, visibility: Union[MapControlVisibility, dict, None] = None, **kwargs: bool
    ) -> MapControlVisibility:
        return super().set_map_control_visibility(visibility, **kwargs)

    def set_split_mode(
        self,
        split_mode: SplitMode,
        options: Union[SplitModeContext, dict, None] = None,
        **kwargs: Any,
    ) -> SplitModeDetails:
        return super().set_split_mode(split_mode, options, **kwargs)
