from typing import List, Optional, Union

from pydantic import BaseModel, Field

from unfolded.map_sdk.api.base import CamelCaseBaseModel
from unfolded.map_sdk.api.dataset_api import (
    DatasetApiInteractiveMixin,
    DatasetApiNonInteractiveMixin,
)
from unfolded.map_sdk.api.event_api import EventApiInteractiveMixin
from unfolded.map_sdk.api.filter_api import (
    FilterApiInteractiveMixin,
    FilterApiNonInteractiveMixin,
)
from unfolded.map_sdk.api.layer_api import (
    LayerApiInteractiveMixin,
    LayerApiNonInteractiveMixin,
)
from unfolded.map_sdk.api.map_api import (
    MapApiInteractiveMixin,
    MapApiNonInteractiveMixin,
    MapStyleCreationProps,
)
from unfolded.map_sdk.environment import default_height
from unfolded.map_sdk.transport.base import (
    BaseInteractiveTransport,
    BaseNonInteractiveTransport,
    BaseTransport,
)


class BasemapParams(CamelCaseBaseModel):
    custom_map_styles: Optional[List[MapStyleCreationProps]]
    initial_map_style_id: Optional[str]


class URLParams(CamelCaseBaseModel):
    static_asset_url_base: Optional[str]
    application_url_base: Optional[str]


# This doesn't subclass from CamelCaseBaseModel because we don't want to mangle key
# names
class MapStyle(BaseModel):
    height: Union[str, float, int] = Field(default_factory=default_height)
    width: Union[str, float, int] = "100%"

    class Config:
        extra = "allow"


class BaseMap:
    """
    Base class for all map types (both widget and non-widget)
    """

    transport: BaseTransport


class BaseInteractiveMap(
    BaseMap,
    MapApiInteractiveMixin,
    DatasetApiInteractiveMixin,
    FilterApiInteractiveMixin,
    LayerApiInteractiveMixin,
    EventApiInteractiveMixin,
):
    transport: BaseInteractiveTransport
    pass


class BaseNonInteractiveMap(
    BaseMap,
    MapApiNonInteractiveMixin,
    DatasetApiNonInteractiveMixin,
    FilterApiNonInteractiveMixin,
    LayerApiNonInteractiveMixin,
):
    transport: BaseNonInteractiveTransport
    pass
