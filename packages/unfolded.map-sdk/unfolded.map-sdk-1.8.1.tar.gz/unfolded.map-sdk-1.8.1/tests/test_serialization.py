from pydantic import parse_obj_as

from unfolded.map_sdk.api.dataset_api import (
    Dataset,
    LocalDataset,
    RasterTileDataset,
    RasterTileLocalItemMetadata,
    VectorTileDataset,
    VectorTileLocalMetadata,
)

from .fixtures.dataset_api import (
    LOCAL_RESPONSE,
    RASTER_TILE_RESPONSE,
    VECTOR_TILE_RESPONSE,
)


class TestDataset:
    """Tests relating to dataset serialization/deserialization"""

    def test_deserialize(self):

        local_dataset = parse_obj_as(Dataset, LOCAL_RESPONSE)
        assert isinstance(local_dataset, LocalDataset)

        vector_tile_dataset = parse_obj_as(Dataset, VECTOR_TILE_RESPONSE)
        assert isinstance(vector_tile_dataset, VectorTileDataset)
        assert isinstance(vector_tile_dataset.metadata, VectorTileLocalMetadata)

        raster_tile_dataset = parse_obj_as(Dataset, RASTER_TILE_RESPONSE)
        assert isinstance(raster_tile_dataset, RasterTileDataset)
        assert isinstance(raster_tile_dataset.metadata, RasterTileLocalItemMetadata)
