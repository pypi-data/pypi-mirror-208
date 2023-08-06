import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import AnyHttpUrl
from pydantic import Field as PydanticField
from pydantic import StrictStr, root_validator, validator

from unfolded.map_sdk.api.base import Action, CamelCaseBaseModel, Number
from unfolded.map_sdk.api.enums import (
    ActionType,
    BasicFieldType,
    DatasetType,
    FieldType,
    TimestampFieldType,
    VectorTileAttributeType,
)
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

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import geopandas as gpd
except ImportError:
    gpd = None


RGBColor = Tuple[Number, Number, Number]
"""Red, green and blue channels of a color in [0-255] range."""


class BaseField(CamelCaseBaseModel):

    name: StrictStr
    """Unique identifier of the field."""

    label: StrictStr
    """User facing field label."""

    type: FieldType
    """Type of the field."""


class BasicField(BaseField):
    """Contains semantics around a single field in a dataset table."""

    type: BasicFieldType


class TimestampField(BaseField):
    """Contains semantics around a single timestamp field in a dataset table."""

    type: TimestampFieldType = TimestampFieldType.TIMESTAMP
    time_format: StrictStr
    """moment.js time format of this field data."""


Field = Union[BasicField, TimestampField]
"""Union of available field types."""


class BaseDataset(CamelCaseBaseModel):

    id: StrictStr
    """Unique identifier of the dataset."""

    type: DatasetType
    """Type of dataset."""

    label: StrictStr
    """Displayable dataset label."""

    color: RGBColor
    """Color label of the dataset."""

    fields: List[Field]
    """Schema describring the fields of the dataset."""


class LocalDataset(BaseDataset):
    """Dataset record representing a local dataset, with data provided by the caller."""

    type = DatasetType.LOCAL


class DatasetWithData(LocalDataset):

    data: List[List[Any]] = PydanticField(..., repr=False)
    """Tabular data backing the dataset, where the order of fields matches the order in `Dataset.fields`."""


class VectorTileBaseMetadata(CamelCaseBaseModel):
    """Vector tileset base metadata."""

    class Config(CamelCaseBaseModel.Config):
        extra = "ignore"

    data_url: AnyHttpUrl
    """URL template for tiles, with {x}/{y}/{z} placeholders"""


class _VectorAttributes(CamelCaseBaseModel):
    """Attributes of a Vector layer."""

    class Config(CamelCaseBaseModel.Config):
        extra = "ignore"

    attribute: StrictStr
    """The name of this attribute."""

    type: VectorTileAttributeType
    """The type of this attribute's values."""

    min: Optional[Number]
    """The minimum value of this attribute (if numeric)."""

    max: Optional[Number]
    """The maximum value of this attribute (if numeric)."""


class _VectorLayer(CamelCaseBaseModel):
    """Layer attribute of the Vector TileJSON."""

    class Config(CamelCaseBaseModel.Config):
        extra = "ignore"

    attributes: List[_VectorAttributes]
    """Attributes in the layer."""


class _VectorTilestats(CamelCaseBaseModel):
    """Tilestats attribute of the Vector TileJSON."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(num_layers={len(self.layers)})"

    class Config(CamelCaseBaseModel.Config):
        extra = "ignore"

    layers: List[_VectorLayer]
    """Layers in the tileset."""


class VectorTileEmbeddedMetadata(CamelCaseBaseModel):
    """Minimal shape for the embedded JSON metadata in a Tippecanoe vector
    tileset metadata file.
    """

    class Config(CamelCaseBaseModel.Config):
        extra = "ignore"

    tilestats: _VectorTilestats
    """The tilestats for this tileset."""


class VectorTileLocalMetadata(VectorTileBaseMetadata):
    """Vector tileset metadata, following the metadata format generated
    by Tippecanoe. This metadata shape can be passed to the
    map to synchronously add a vector tileset.
    see https://github.com/mapbox/tippecanoe
    """

    # JSON metadata has multiple names in different contexts
    # maxzoom and minzoom are returned by studio in camelCase
    @root_validator(pre=True)
    # pylint:disable=no-self-argument
    def allow_alternate_aliases(cls, values):
        if not values.get("json"):
            values["json"] = values.get("metaJson")

        if not values.get("maxzoom"):
            values["maxzoom"] = values.get("maxZoom")

        if not values.get("minzoom"):
            values["minzoom"] = values.get("minZoom")

        return values

    class Config(VectorTileBaseMetadata.Config):
        extra = "ignore"

    metadata_url: Optional[AnyHttpUrl]
    """URL for tileset metadata."""

    bounds: Optional[Union[StrictStr, List[Number]]]
    """Tileset bounds, as an array or comma-delimited string in format "w,s,e,n"."""

    center: Optional[Union[StrictStr, List[Number]]]
    """Tileset center, as an array or comma-delimited string in format "lng,lat"."""

    maxzoom: Optional[Number]
    """Maximum zoom supported by the tileset."""

    minzoom: Optional[Number]
    """Minimum zoom supported by the tileset."""

    _json: Union[StrictStr, VectorTileEmbeddedMetadata, None] = PydanticField(
        ..., alias="json"
    )
    """Metadata for the tileset, as a JSON string or object."""


class VectorTileRemoteMetadata(VectorTileBaseMetadata):
    """Vector tileset metadata with a remote metadata URL. The remote metadata file
    should follow the metadata format generated by Tippecanoe. This metadata can
    be passed to the map to asynchronously load a vector tileset.
    see https://github.com/mapbox/tippecanoe
    """

    metadata_url: AnyHttpUrl
    """URL for tileset metadata."""


VectorTileMetadata = Union[VectorTileLocalMetadata, VectorTileRemoteMetadata]


class VectorTileDataset(BaseDataset):
    """Dataset record representing a vector tileset."""

    type = DatasetType.VECTOR_TILE

    metadata: VectorTileMetadata
    """Metadata about the vector tileset."""


class RasterTileBaseMetadata(CamelCaseBaseModel):
    """Raster tileset base metadata."""

    class Config(CamelCaseBaseModel.Config):
        extra = "allow"


class RasterTileLocalItemMetadata(RasterTileBaseMetadata):
    """Raster tileset metadata in STAC Item format. STAC version must be >= 1.0.0,
    and the EO and Raster STAC extensions are required. This metadata shape can
    be passed to the map to synchronously add a raster tileset.
    see https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md
    """

    # pylint:disable=no-self-argument

    type: Literal["Feature"]
    """Type of the raster tileset."""

    stac_version: StrictStr = PydanticField(..., alias="stac_version")
    """STAC version for tileset."""

    stac_extensions: List[StrictStr] = PydanticField(..., alias="stac_extensions")
    """A list of extensions the Item implements."""

    assets: Dict[StrictStr, Any]
    """Dictionary of asset objects that can be downloaded, each with a unique key."""

    @validator("stac_version")
    def validate_stac_version(cls, v: str):
        if v[0] == "0":
            raise ValueError("stac_version must be 1.0 or higher")

        return v

    @validator("stac_extensions")
    def validate_stac_extensions(cls, v: List[str]):
        extension_regex = (
            r"https://stac-extensions.github.io/{ext}/v1\.\d\.\d/schema\.json"
        )
        if not any(re.match(extension_regex.format(ext="eo"), s) for s in v):
            raise ValueError("STAC eo extension, 1.0 or higher, is required")

        if not any(re.match(extension_regex.format(ext="raster"), s) for s in v):
            raise ValueError("STAC raster extension, 1.0 or higher, is required")

        return v


class RasterTileLocalCollectionMetadata(RasterTileBaseMetadata):
    # pylint:disable=no-self-argument

    type: Literal["Collection"]

    stac_version: StrictStr = PydanticField(..., alias="stac_version")
    """STAC version for tileset."""

    stac_extensions: List[StrictStr] = PydanticField(..., alias="stac_extensions")
    """A list of extensions the Item implements."""

    item_assets: Dict[StrictStr, Any] = PydanticField(..., alias="item_assets")
    """Dictionary of asset objects that items in the collection expose, each with a unique key."""

    @validator("stac_version")
    def validate_stac_version(cls, v: str):
        if v[0] == "0":
            raise ValueError("stac_version must be 1.0 or higher")

        return v

    @validator("stac_extensions")
    def validate_stac_extensions(cls, v: List[str]):
        extension_regex = (
            r"https://stac-extensions.github.io/{ext}/v1\.\d\.\d/schema\.json"
        )
        if not any(re.match(extension_regex.format(ext="eo"), s) for s in v):
            raise ValueError("STAC eo extension, 1.0 or higher, is required")

        if not any(re.match(extension_regex.format(ext="raster"), s) for s in v):
            raise ValueError("STAC raster extension, 1.0 or higher, is required")

        if not any(re.match(extension_regex.format(ext="item-assets"), s) for s in v):
            raise ValueError("STAC item-assets extension, 1.0 or higher, is required")

        return v


RasterTileLocalMetadata = Union[
    RasterTileLocalItemMetadata, RasterTileLocalCollectionMetadata
]


class RasterTileRemoteMetadata(RasterTileBaseMetadata):
    """Raster tileset metadata with a remote metadata URL. This metadata can
    be passed to the map to asynchronously load a raster tileset.
    """

    metadata_url: AnyHttpUrl
    """URL for tileset metadata."""


RasterTileMetadata = Union[RasterTileLocalMetadata, RasterTileRemoteMetadata]


class RasterTileDataset(BaseDataset):
    """Dataset record representing a raster tileset."""

    type = DatasetType.RASTER_TILE

    metadata: RasterTileMetadata
    """Metadata about the raster tileset."""


Dataset = Union[LocalDataset, VectorTileDataset, RasterTileDataset]


class _BaseDatasetCreationProps(CamelCaseBaseModel):

    id: Optional[StrictStr]
    """Unique identifier of the dataset."""

    type: DatasetType
    """Type of dataset."""

    label: Optional[StrictStr]
    """Displayable dataset label."""

    color: Optional[RGBColor]
    """Color label of the dataset."""


class _LocalDatasetCreationProps(_BaseDatasetCreationProps):
    """A set of properties used to create a dataset with inline data."""

    type: DatasetType = PydanticField(default=DatasetType.LOCAL)

    data: Union[StrictStr, dict, List[List[Any]]]
    """Data used to create a dataset, in CSV, JSON, GeoJSON format."""


class _VectorTileDatasetCreationProps(_BaseDatasetCreationProps):
    """A set of properties used to create a vector tile dataset with provided metadata."""

    type: DatasetType = DatasetType.VECTOR_TILE

    metadata: VectorTileLocalMetadata
    """Metadata about the vector tileset."""


class _VectorTileDatasetRemoteCreationProps(_BaseDatasetCreationProps):
    """A set of properties used to create a vector tile dataset with remote metadata."""

    type: DatasetType = DatasetType.VECTOR_TILE

    metadata: VectorTileRemoteMetadata
    """Metadata about the vector tileset."""


class _RasterTileDatasetCreationProps(_BaseDatasetCreationProps):
    """A set of properties used to create a raster tile dataset with provided metadata."""

    type: DatasetType = DatasetType.RASTER_TILE

    metadata: RasterTileLocalMetadata
    """Metadata about the raster tileset."""


class _RasterTileDatasetRemoteCreationProps(_BaseDatasetCreationProps):
    """A set of properties used to create a raster tile dataset with remote metadata."""

    type: DatasetType = DatasetType.RASTER_TILE

    metadata: RasterTileRemoteMetadata
    """Metadata about the raster tileset."""


_DatasetCreationProps = Union[
    _LocalDatasetCreationProps,
    _VectorTileDatasetCreationProps,
    _RasterTileDatasetCreationProps,
]


_TileDatasetCreationProps = Union[
    _VectorTileDatasetRemoteCreationProps, _RasterTileDatasetRemoteCreationProps
]


class _DatasetUpdateProps(CamelCaseBaseModel):
    """A set of properties used to update a dataset."""

    label: Optional[StrictStr]
    """Displayable dataset label."""

    color: Optional[RGBColor]
    """Color label of the dataset."""


###########
# ACTIONS #
###########


class GetDatasetsAction(Action):
    """Action payload sent with `get_datasets` calls"""

    type = ActionType.GET_DATASETS


class GetDatasetByIdAction(Action):
    """Action payload sent with `get_dataset_by_id` calls"""

    class Meta(Action.Meta):
        args = ["dataset_id"]

    type = ActionType.GET_DATASET_BY_ID
    dataset_id: StrictStr


class AddDatasetAction(Action):
    """Action payload sent with `add_dataset` calls"""

    class Meta(Action.Meta):
        args = ["dataset"]
        options = ["auto_create_layers", "center_map"]

    type = ActionType.ADD_DATASET
    dataset: _DatasetCreationProps
    auto_create_layers: bool
    center_map: bool


class AddTileDatasetAction(Action):
    """Action payload sent with `add_tile_dataset` calls"""

    class Meta(Action.Meta):
        args = ["dataset"]
        options = ["auto_create_layers", "center_map"]

    type = ActionType.ADD_TILE_DATASET
    dataset: _TileDatasetCreationProps
    auto_create_layers: bool
    center_map: bool


class UpdateDatasetAction(Action):
    """Action payload sent with `update_dataset` calls"""

    class Meta(Action.Meta):
        args = ["dataset_id", "values"]

    type = ActionType.UPDATE_DATASET
    dataset_id: StrictStr
    values: _DatasetUpdateProps


class RemoveDatasetAction(Action):
    """Action payload sent with `remove_dataset` calls"""

    class Meta(Action.Meta):
        args = ["dataset_id"]

    type = ActionType.REMOVE_DATASET
    dataset_id: StrictStr


class ReplaceDatasetAction(Action):
    """Action payload sent with `replace_dataset` calls"""

    class Meta(Action.Meta):
        args = ["this_dataset_id", "with_dataset"]
        options = ["force", "strict"]

    type = ActionType.REPLACE_DATASET
    this_dataset_id: StrictStr
    with_dataset: _DatasetCreationProps
    force: bool
    strict: bool


class GetDatasetWithDataAction(Action):
    """Action payload sent with `get_dataset_with_data` calls"""

    class Meta(Action.Meta):
        args = ["dataset_id"]

    type = ActionType.GET_DATASET_WITH_DATA
    dataset_id: StrictStr


#########
# UTILS #
#########


def normalize_dataset(
    dataset: Union[Dataset, Dict, None],
    kwargs: Dict[str, Any],
    fields_to_exclude: Optional[List[str]] = None,
) -> Dict:
    # convert to dict to make transformations
    if isinstance(dataset, BaseDataset):
        dataset_dict = dataset.dict(exclude_none=True)
    elif dataset is not None and isinstance(dataset, dict):
        dataset_dict = dataset
    else:
        dataset_dict = kwargs

    if fields_to_exclude:
        for field in fields_to_exclude:
            if field in dataset_dict:
                del dataset_dict[field]

    return dataset_dict


def normalize_data(
    data: Union[str, dict, List[List[Any]], "pd.DataFrame", "gpd.GeoDataFrame"]
) -> Union[str, dict, List[List[Any]]]:

    if gpd is not None and isinstance(data, gpd.GeoDataFrame):
        # convert to GeoJSON FeatureCollection
        return json.loads(data.to_json())
    elif pd is not None and isinstance(data, pd.DataFrame):
        # convert to CSV string
        return data.to_csv()
    else:
        return data


###########
# METHODS #
###########


class BaseDatasetApiMethods:

    transport: BaseTransport

    @validate_kwargs(positional_only=["dataset"])
    def add_dataset(
        self,
        dataset: Union[Dataset, Dict, None] = None,
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
        **kwargs: Any,
    ) -> Optional[Dataset]:
        """Adds a new dataset to the map.

        Args:
            dataset:
                A dictionary with the following format. Unused if these attributes are provided through kwargs.
                    id (Optional[str]): Unique identifier of the dataset. If not provided, a random id will be generated.
                    label (Optional[str]): Displayable dataset label.
                    color: (Optional[Tuple[float, float, float]]): Color label of the dataset
                    data: (Union[str, dict, List[List[Any]]]): Data used to create a dataset, in CSV, JSON, or GeoJSON format (for local datasets).
                    metadata: (Dict): Object containing tileset metadata (for tiled datasets).

        Kwargs:
            auto_create_layers:
                Whether to attempt and create new layer(s) when adding a dataset. Defaults to True.
            center_map:
                Whether to center the map to fit the new layer bounds. Defaults to True.
            id (Optional[str]): Unique identifier of the dataset. If not provided, a random id will be generated.
            label (Optional[str]): Displayable dataset label.
            color: (Optional[Tuple[float, float, float]]): Color label of the dataset
            data: (Union[str, dict, List[List[Any]]]): Data used to create a dataset, in CSV, JSON, or GeoJSON format (for local datasets).
            metadata: (Dict): Object containing tileset metadata (for tiled datasets).

        Returns (widget map only):
            Dataset: The newly created dataset.
        """

        dataset = normalize_dataset(dataset, kwargs, ["fields"])

        if "data" in dataset:
            dataset["data"] = normalize_data(dataset["data"])

        action = AddDatasetAction(
            dataset=dataset,
            auto_create_layers=auto_create_layers,
            center_map=center_map,
        )
        return self.transport.send_action_non_null(
            action=action, response_class=Dataset  # type: ignore[arg-type]
        )

    @validate_kwargs(positional_only=["dataset"])
    def add_tile_dataset(
        self,
        dataset: Union[Dataset, Dict, None] = None,
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
        **kwargs: Any,
    ) -> Optional[Dataset]:
        """Adds a new dataset to the map.

        Args:
            dataset:
                A dictionary with the following format. Unused if these attributes are provided through kwargs.
                    id (Optional[str]): Unique identifier of the dataset. If not provided, a random id will be generated.
                    label (Optional[str]): Displayable dataset label.
                    color: (Optional[Tuple[float, float, float]]): Color label of the dataset
                    metadata: (Dict): Object containing tileset metadata.

        Kwargs:
            auto_create_layers:
                Whether to attempt and create new layer(s) when adding a dataset. Defaults to True.
            center_map:
                Whether to center the map to fit the new layer bounds. Defaults to True.
            id (Optional[str]): Unique identifier of the dataset. If not provided, a random id will be generated.
            label (Optional[str]): Displayable dataset label.
            color: (Optional[Tuple[float, float, float]]): Color label of the dataset
            metadata: (Dict): Object containing tileset metadata.

        Returns (widget map only):
            Dataset: The newly created dataset.
        """

        dataset = normalize_dataset(dataset, kwargs, ["fields", "data"])

        action = AddTileDatasetAction(
            dataset=dataset,
            auto_create_layers=auto_create_layers,
            center_map=center_map,
        )

        # Fails mypy because Dataset is a Union
        return self.transport.send_action_non_null(
            action=action, response_class=Dataset  # type: ignore[arg-type]
        )

    @validate_kwargs(positional_only=["dataset_id", "values"])
    def update_dataset(
        self,
        dataset_id: str,
        values: Union[_DatasetUpdateProps, dict, None] = None,
        **kwargs: Any,
    ) -> Optional[Dataset]:
        """Updates an existing dataset with given values.

        Args:
            dataset_id: The identifier of the dataset to update.
            values: The values to update.

        Kwargs:
            label: Displayable dataset label.
            color: Color label of the dataset.

        Returns (widget map only):
            Dataset: Updated dataset record.
        """

        action = UpdateDatasetAction(
            dataset_id=dataset_id, values=values if values else kwargs
        )

        # Fails mypy because Dataset is a Union
        return self.transport.send_action_non_null(
            action=action, response_class=Dataset  # type: ignore[arg-type]
        )

    @validate_kwargs(positional_only=["dataset_id"])
    def remove_dataset(self, dataset_id: str) -> None:
        """Removes a dataset from the map.

        Args:
            dataset_id: The identifier of the dataset to remove.

        Returns:
            None
        """
        action = RemoveDatasetAction(dataset_id=dataset_id)
        self.transport.send_action(action=action, response_class=None)

    @validate_kwargs(positional_only=["this_dataset_id", "with_dataset"])
    def replace_dataset(
        self,
        this_dataset_id: str,
        with_dataset: Union[Dataset, Dict, None] = None,
        *,
        force: bool = False,
        strict: bool = False,
        **kwargs: Any,
    ) -> Optional[Dataset]:
        """Replaces a given dataset with a new one.

        Args:
            this_dataset_id: Identifier of the dataset to replace.
            with_dataset: Dataset details to replace the dataset with.

        Kwargs:
            force:
                Whether to force a dataset replace, even if the compatibility check fails. Defaults to False.
            strict:
                Whether to ensure strict equality of types for each field being replaced. Defaults to False.

        Returns (widget map only):
            Dataset: The dataset that's now in use.
        """
        with_dataset = normalize_dataset(with_dataset, kwargs, ["fields"])

        if "data" in with_dataset:
            with_dataset["data"] = normalize_data(with_dataset["data"])

        action = ReplaceDatasetAction(
            this_dataset_id=this_dataset_id,
            with_dataset=with_dataset,
            force=force,
            strict=strict,
        )

        # Fails mypy because Dataset is a Union
        return self.transport.send_action_non_null(
            action=action, response_class=Dataset  # type: ignore[arg-type]
        )


class BaseInteractiveDatasetApiMethods:

    transport: BaseInteractiveTransport

    def get_datasets(self) -> List[Dataset]:
        """Gets all the datasets currently available in the map.

        Returns:
            An array of datasets.
        """
        action = GetDatasetsAction()
        return self.transport.send_action_non_null(
            action=action, response_class=List[Dataset]
        )

    @validate_kwargs(positional_only=["dataset_id"])
    def get_dataset_by_id(self, dataset_id: str) -> Optional[Dataset]:
        """Retrieves a dataset by its identifier if it exists.

        Args:
            dataset_id: Identifier of the dataset to get.

        Returns:
            Dataset with a given identifier, or null if one doesn't exist.
        """
        action = GetDatasetByIdAction(dataset_id=dataset_id)
        return self.transport.send_action(action=action, response_class=Dataset)  # type: ignore[arg-type]

    @validate_kwargs(positional_only=["dataset_id"])
    def get_dataset_with_data(self, dataset_id: str) -> Optional[DatasetWithData]:
        """Retrieves a dataset record with its data for a given dataset if it exists.

        Args:
            dataset_id: Identifier of the dataset to get the record for.

        Returns:
            Dataset record with its data based on an identifier, or None if one doesn't exist.
        """
        action = GetDatasetWithDataAction(dataset_id=dataset_id)
        return self.transport.send_action(action=action, response_class=DatasetWithData)


class DatasetApiNonInteractiveMixin(BaseDatasetApiMethods):
    """Dataset methods that are supported in non-interactive (i.e. pure HTML) maps"""

    transport: BaseNonInteractiveTransport

    def add_dataset(
        self,
        dataset: Union[Dataset, Dict, None] = None,
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
        **kwargs: Any,
    ) -> None:
        super().add_dataset(
            dataset,
            auto_create_layers=auto_create_layers,
            center_map=center_map,
            **kwargs,
        )
        return

    def add_tile_dataset(
        self,
        dataset: Union[Dataset, Dict, None] = None,
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
        **kwargs: Any,
    ) -> None:
        super().add_tile_dataset(
            dataset,
            auto_create_layers=auto_create_layers,
            center_map=center_map,
            **kwargs,
        )
        return

    def update_dataset(
        self,
        dataset_id: str,
        values: Union[_DatasetUpdateProps, dict, None] = None,
        **kwargs: Any,
    ) -> None:
        super().update_dataset(dataset_id, values, **kwargs)
        return

    def replace_dataset(
        self,
        this_dataset_id: str,
        with_dataset: Union[Dataset, Dict, None] = None,
        **kwargs: Any,
    ) -> None:
        super().replace_dataset(this_dataset_id, with_dataset, **kwargs)
        return


class DatasetApiInteractiveMixin(
    BaseDatasetApiMethods, BaseInteractiveDatasetApiMethods
):

    transport: BaseInteractiveTransport

    def add_dataset(
        self,
        dataset: Union[Dataset, Dict, None] = None,
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
        **kwargs: Any,
    ) -> Dataset:
        return super().add_dataset(
            dataset,
            auto_create_layers=auto_create_layers,
            center_map=center_map,
            **kwargs,
        )

    def add_tile_dataset(
        self,
        dataset: Union[Dataset, Dict, None] = None,
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
        **kwargs: Any,
    ) -> Dataset:
        return super().add_tile_dataset(
            dataset,
            auto_create_layers=auto_create_layers,
            center_map=center_map,
            **kwargs,
        )

    def update_dataset(
        self,
        dataset_id: str,
        values: Union[_DatasetUpdateProps, dict, None] = None,
        **kwargs: Any,
    ) -> Dataset:
        return super().update_dataset(dataset_id, values, **kwargs)

    def replace_dataset(
        self,
        this_dataset_id: str,
        with_dataset: Union[Dataset, Dict, None] = None,
        **kwargs: Any,
    ) -> Dataset:
        return super().replace_dataset(this_dataset_id, with_dataset, **kwargs)
