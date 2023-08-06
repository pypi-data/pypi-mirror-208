from tests._utils import check_expected_comm_message
from tests.conftest import MockComm
from unfolded.map_sdk.map.widget import SyncWidgetMap

DATASET_UUID = "0e939627-8ea7-4db6-8c92-3dd943166a01"
FILTER_UUID = "e02b67ea-20d4-4613-808e-9a8fdbd81e6f"


class TestGetFilters:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_filters()

        expected = {
            "type": "v1/map-sdk-get-filters",
            "args": [],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestGetFilterById:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_filter_by_id(FILTER_UUID)

        expected = {
            "type": "v1/map-sdk-get-filter-by-id",
            "args": [FILTER_UUID],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestAddFilter:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-add-filter",
            "args": [
                {
                    "type": "range",
                    "sources": [{"dataId": DATASET_UUID, "fieldName": "test"}],
                    "value": [0, 100],
                }
            ],
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        filter_ = {
            "type": "range",
            "sources": [{"data_id": DATASET_UUID, "field_name": "test"}],
            "value": (0, 100),
        }
        mock_widget_map.add_filter(filter_)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        filter_ = {
            "type": "range",
            "sources": [{"data_id": DATASET_UUID, "field_name": "test"}],
            "value": (0, 100),
        }
        mock_widget_map.add_filter(**filter_)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestUpdateFilter:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-update-filter",
            "args": [
                FILTER_UUID,
                {
                    "type": "range",
                    "value": [0, 50],
                    "sources": [{"dataId": DATASET_UUID, "fieldName": "test-2"}],
                },
            ],
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        values = {
            "value": (0, 50),
            "sources": [{"data_id": DATASET_UUID, "field_name": "test-2"}],
        }
        mock_widget_map.update_filter(FILTER_UUID, values)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        values = {
            "value": (0, 50),
            "sources": [{"data_id": DATASET_UUID, "field_name": "test-2"}],
        }
        mock_widget_map.update_filter(FILTER_UUID, **values)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestRemoveFilter:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.remove_filter(FILTER_UUID)

        expected = {
            "type": "v1/map-sdk-remove-filter",
            "args": [FILTER_UUID],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestUpdateTimeline:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-update-timeline",
            "args": [FILTER_UUID, {"view": "side", "isAnimating": True}],
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        values = {"view": "side", "is_animating": True}
        mock_widget_map.update_timeline(FILTER_UUID, values)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        values = {"view": "side", "is_animating": True}
        mock_widget_map.update_timeline(FILTER_UUID, **values)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)
