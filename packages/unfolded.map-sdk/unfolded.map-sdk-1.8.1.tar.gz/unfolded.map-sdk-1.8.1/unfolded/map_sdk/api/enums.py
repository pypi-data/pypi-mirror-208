from enum import Enum
from typing import Dict

MESSAGE_PREFIX = "v1/"


class ActionType(str, Enum):
    """Actions that can be passed to Studio.

    Must be kept in sync with enum in
    python/modules/map-sdk/src/message-handling.ts
    """

    # Map API
    GET_VIEW = f"{MESSAGE_PREFIX}map-sdk-get-view"
    SET_VIEW = f"{MESSAGE_PREFIX}map-sdk-set-view"
    GET_VIEW_LIMITS = f"{MESSAGE_PREFIX}map-sdk-get-view-limits"
    SET_VIEW_LIMITS = f"{MESSAGE_PREFIX}map-sdk-set-view-limits"
    GET_MAP_CONTROL_VISIBILITY = f"{MESSAGE_PREFIX}map-sdk-get-map-control-visibility"
    SET_MAP_CONTROL_VISIBILITY = f"{MESSAGE_PREFIX}map-sdk-set-map-control-visibility"
    GET_SPLIT_MODE = f"{MESSAGE_PREFIX}map-sdk-get-split-mode"
    SET_SPLIT_MODE = f"{MESSAGE_PREFIX}map-sdk-set-split-mode"
    SET_THEME = f"{MESSAGE_PREFIX}map-sdk-set-theme"
    GET_MAP_CONFIG = f"{MESSAGE_PREFIX}map-sdk-get-map-config"
    SET_MAP_CONFIG = f"{MESSAGE_PREFIX}map-sdk-set-map-config"
    GET_MAP_STYLES = f"{MESSAGE_PREFIX}map-sdk-get-map-styles"

    # Filter API
    GET_FILTERS = f"{MESSAGE_PREFIX}map-sdk-get-filters"
    GET_FILTER_BY_ID = f"{MESSAGE_PREFIX}map-sdk-get-filter-by-id"
    ADD_FILTER = f"{MESSAGE_PREFIX}map-sdk-add-filter"
    UPDATE_FILTER = f"{MESSAGE_PREFIX}map-sdk-update-filter"
    REMOVE_FILTER = f"{MESSAGE_PREFIX}map-sdk-remove-filter"
    UPDATE_TIMELINE = f"{MESSAGE_PREFIX}map-sdk-update-timeline"

    # Datasets API
    GET_DATASETS = f"{MESSAGE_PREFIX}map-sdk-get-datasets"
    GET_DATASET_BY_ID = f"{MESSAGE_PREFIX}map-sdk-get-dataset-by-id"
    ADD_DATASET = f"{MESSAGE_PREFIX}map-sdk-add-dataset"
    ADD_TILE_DATASET = f"{MESSAGE_PREFIX}map-sdk-add-tile-dataset"
    UPDATE_DATASET = f"{MESSAGE_PREFIX}map-sdk-update-dataset"
    REMOVE_DATASET = f"{MESSAGE_PREFIX}map-sdk-remove-dataset"
    REPLACE_DATASET = f"{MESSAGE_PREFIX}map-sdk-replace-dataset"
    GET_DATASET_WITH_DATA = f"{MESSAGE_PREFIX}map-sdk-get-dataset-with-data"

    # Layer API
    GET_LAYERS = f"{MESSAGE_PREFIX}map-sdk-get-layers"
    GET_LAYER_BY_ID = f"{MESSAGE_PREFIX}map-sdk-get-layer-by-id"
    ADD_LAYER = f"{MESSAGE_PREFIX}map-sdk-add-layer"
    UPDATE_LAYER = f"{MESSAGE_PREFIX}map-sdk-update-layer"
    REMOVE_LAYER = f"{MESSAGE_PREFIX}map-sdk-remove-layer"
    GET_LAYER_GROUPS = f"{MESSAGE_PREFIX}map-sdk-get-layer-groups"
    GET_LAYER_GROUP_BY_ID = f"{MESSAGE_PREFIX}map-sdk-get-layer-group-by-id"
    ADD_LAYER_GROUP = f"{MESSAGE_PREFIX}map-sdk-add-layer-group"
    UPDATE_LAYER_GROUP = f"{MESSAGE_PREFIX}map-sdk-update-layer-group"
    REMOVE_LAYER_GROUP = f"{MESSAGE_PREFIX}map-sdk-remove-layer-group"
    GET_LAYER_TIMELINE = f"{MESSAGE_PREFIX}map-sdk-get-layer-timeline"
    UPDATE_LAYER_TIMELINE = f"{MESSAGE_PREFIX}map-sdk-update-layer-timeline"

    # Event API
    SET_EVENT_HANDLERS = f"{MESSAGE_PREFIX}map-sdk-set-event-handlers"
    REMOVE_EVENT_HANDLERS = f"{MESSAGE_PREFIX}map-sdk-remove-event-handlers"


class DatasetType(str, Enum):
    """Types of currently support datasets."""

    LOCAL = "local"
    VECTOR_TILE = "vector-tile"
    RASTER_TILE = "raster-tile"


class VectorTileAttributeType(str, Enum):
    """Types of Tippecanoe vector tileset attributes"""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"


class FilterType(str, Enum):
    """Types of currently supported filters."""

    RANGE = "range"
    SELECT = "select"
    TIME_RANGE = "time-range"
    MULTI_SELECT = "multi-select"


class FieldType(str, Enum):
    pass


class BasicFieldType(FieldType):

    BOOLEAN = "boolean"
    DATE = "date"
    GEOJSON = "geojson"
    INTEGER = "integer"
    REAL = "real"
    STRING = "string"
    ARRAY = "array"
    OBJECT = "object"
    POINT = "point"
    H3 = "h3"


class TimestampFieldType(FieldType):

    TIMESTAMP = "timestamp"


class LayerType(str, Enum):
    """Types of layers that the visualization is supported for."""

    POINT = "point"
    ARC = "arc"
    LINE = "line"
    GRID = "grid"
    HEXAGON = "hexagon"
    GEOJSON = "geojson"
    CLUSTER = "cluster"
    ICON = "icon"
    HEATMAP = "heatmap"
    H3 = "h3"
    THREE_D = "three-d"
    TRIP = "trip"
    S2 = "s2"
    RASTER_TILE = "raster-tile"
    VECTOR_TILE = "vector-tile"


class EventType(str, Enum):
    """Events that can be received from Studio.

    Must be kept in sync with enum in
    python/modules/map-sdk/src/message-handling.ts
    """

    # Map API
    ON_CLICK = f"{MESSAGE_PREFIX}map-sdk-on-click"
    ON_HOVER = f"{MESSAGE_PREFIX}map-sdk-on-hover"
    ON_VIEW_UPDATE = f"{MESSAGE_PREFIX}map-sdk-on-view-update"
    ON_GEOMETRY_SELECTION = f"{MESSAGE_PREFIX}map-sdk-on-geometry-selection"

    # Layer API
    ON_LAYER_TIMELINE_UPDATE = f"{MESSAGE_PREFIX}map-sdk-on-layer-timeline-update"

    # Filter API
    ON_FILTER_UPDATE = f"{MESSAGE_PREFIX}map-sdk-on-filter-update"

    # Extra
    ON_LOAD = f"{MESSAGE_PREFIX}map-sdk-on-load"


EVENT_HANDLER_MAP: Dict[str, EventType] = {
    "on_click": EventType.ON_CLICK,
    "on_hover": EventType.ON_HOVER,
    "on_view_update": EventType.ON_VIEW_UPDATE,
    "on_geometry_selection": EventType.ON_GEOMETRY_SELECTION,
    "on_layer_timeline_update": EventType.ON_LAYER_TIMELINE_UPDATE,
    "on_filter_update": EventType.ON_FILTER_UPDATE,
    "on_load": EventType.ON_LOAD,
}


REVERSE_EVENT_HANDLER_MAP: Dict[EventType, str] = {
    v: k for k, v in EVENT_HANDLER_MAP.items()
}


def is_event_type(event_type: str) -> bool:
    try:
        EventType(event_type)
    except ValueError:
        return False
    return True
