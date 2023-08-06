from tests._utils import check_expected_comm_message
from tests.conftest import MockComm
from unfolded.map_sdk.map.widget import SyncWidgetMap


class TestGetDatasets:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_datasets()

        expected = {
            "type": "v1/map-sdk-get-datasets",
            "args": [],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestGetDatasetById:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_dataset_by_id("dataset-id")

        expected = {
            "type": "v1/map-sdk-get-dataset-by-id",
            "args": ["dataset-id"],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestAddDataset:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-add-dataset",
            "args": [
                {
                    "id": "dataset-id",
                    "type": "local",
                    "label": "dataset-label",
                    "data": "dataset data",
                }
            ],
            "options": {
                "autoCreateLayers": False,
                "centerMap": False,
            },
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        dataset = {
            "id": "dataset-id",
            "type": "local",
            "label": "dataset-label",
            "data": "dataset data",
        }
        auto_create_layers = False
        center_map = False

        mock_widget_map.add_dataset(
            dataset, auto_create_layers=auto_create_layers, center_map=center_map
        )

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        dataset = {
            "id": "dataset-id",
            "type": "local",
            "label": "dataset-label",
            "data": "dataset data",
        }
        auto_create_layers = False
        center_map = False

        mock_widget_map.add_dataset(
            **dataset, auto_create_layers=auto_create_layers, center_map=center_map
        )

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_raster_custom_stac_item(
        self,
        mock_comm: MockComm,
        sentinel2_stac_item: dict,
        mock_widget_map: SyncWidgetMap,
    ):
        raster_tile_dataset = {"type": "raster-tile", "metadata": sentinel2_stac_item}
        mock_widget_map.add_dataset(raster_tile_dataset)

        expected = {
            "type": "v1/map-sdk-add-dataset",
            "args": [{"type": "raster-tile", "metadata": sentinel2_stac_item}],
            "options": {"autoCreateLayers": True, "centerMap": True},
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)

    def test_raster_custom_stac_collection(
        self,
        mock_comm: MockComm,
        sentinel2_stac_collection: dict,
        mock_widget_map: SyncWidgetMap,
    ):
        raster_tile_dataset = {
            "type": "raster-tile",
            "metadata": sentinel2_stac_collection,
        }
        mock_widget_map.add_dataset(raster_tile_dataset)

        expected = {
            "type": "v1/map-sdk-add-dataset",
            "args": [{"type": "raster-tile", "metadata": sentinel2_stac_collection}],
            "options": {"autoCreateLayers": True, "centerMap": True},
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestAddTileDataset:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-add-tile-dataset",
            "args": [
                {
                    "id": "dataset-id",
                    "type": "vector-tile",
                    "label": "dataset-label",
                    "metadata": {
                        "metadataUrl": "http://example.com",
                    },
                }
            ],
            "options": {
                "autoCreateLayers": False,
                "centerMap": False,
            },
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        dataset = {
            "id": "dataset-id",
            "type": "vector-tile",
            "label": "dataset-label",
            "metadata": {
                "metadata_url": "http://example.com",
            },
        }
        auto_create_layers = False
        center_map = False

        mock_widget_map.add_tile_dataset(
            dataset, auto_create_layers=auto_create_layers, center_map=center_map
        )

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        dataset = {
            "id": "dataset-id",
            "type": "vector-tile",
            "label": "dataset-label",
            "metadata": {
                "metadata_url": "http://example.com",
            },
        }
        auto_create_layers = False
        center_map = False

        mock_widget_map.add_tile_dataset(
            **dataset, auto_create_layers=auto_create_layers, center_map=center_map
        )

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestUpdateDataset:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-update-dataset",
            "args": [
                "dataset-id",
                {
                    "label": "new-label",
                    "color": [0, 1, 0],
                },
            ],
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.update_dataset(
            "dataset-id",
            {
                "label": "new-label",
                "color": [0, 1, 0],
            },
        )

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        mock_widget_map.update_dataset(
            "dataset-id",
            **{
                "label": "new-label",
                "color": [0, 1, 0],
            },
        )

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestRemoveDataset:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.remove_dataset("dataset-id")

        expected = {
            "type": "v1/map-sdk-remove-dataset",
            "args": [
                "dataset-id",
            ],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestReplaceDataset:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-replace-dataset",
            "args": [
                "dataset-id",
                {
                    "id": "dataset-id",
                    "type": "local",
                    "label": "dataset-label",
                    "data": "dataset data",
                },
            ],
            "options": {"force": False, "strict": False},
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.replace_dataset(
            "dataset-id",
            {
                "id": "dataset-id",
                "type": "local",
                "label": "dataset-label",
                "data": "dataset data",
            },
        )

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        mock_widget_map.replace_dataset(
            "dataset-id",
            **{
                "id": "dataset-id",
                "type": "local",
                "label": "dataset-label",
                "data": "dataset data",
            },
        )

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestGetDatasetWithData:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_dataset_with_data("dataset-id")

        expected = {
            "type": "v1/map-sdk-get-dataset-with-data",
            "args": [
                "dataset-id",
            ],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)
