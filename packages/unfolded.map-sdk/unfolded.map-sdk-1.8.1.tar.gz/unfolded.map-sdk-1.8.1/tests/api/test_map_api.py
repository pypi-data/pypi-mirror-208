from tests._utils import check_expected_comm_message
from tests.conftest import MockComm
from unfolded.map_sdk.map.widget import SyncWidgetMap

LAYER_UUID = "997c21eb-604b-49df-add9-b2fcc615a243"


class TestGetView:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_view(0)

        expected = {
            "type": "v1/map-sdk-get-view",
            "args": [0],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestSetView:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-set-view",
            "args": [
                {
                    "longitude": 8.650367,
                    "latitude": 47.271057,
                    "zoom": 5.0,
                }
            ],
            "options": {"index": 0},
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        view = {"latitude": 47.271057, "longitude": 8.650367, "zoom": 5}
        mock_widget_map.set_view(view, 0)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        view = {"latitude": 47.271057, "longitude": 8.650367, "zoom": 5}
        mock_widget_map.set_view(**view, index=0)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestGetViewLimits:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_view_limits(0)

        expected = {
            "type": "v1/map-sdk-get-view-limits",
            "args": [0],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestSetViewLimits:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-set-view-limits",
            "args": [
                {
                    "minZoom": 3,
                    "maxZoom": 8,
                }
            ],
            "options": {"index": 0},
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        view_limits = {"min_zoom": 3, "max_zoom": 8}
        mock_widget_map.set_view_limits(view_limits, 0)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        view_limits = {"min_zoom": 3, "max_zoom": 8}
        mock_widget_map.set_view_limits(**view_limits, index=0)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestGetMapControlVisibility:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_map_control_visibility()

        expected = {
            "type": "v1/map-sdk-get-map-control-visibility",
            "args": [],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestSetMapControlVisibility:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-set-map-control-visibility",
            "args": [
                {
                    "legend": False,
                    "toggle-3d": True,
                }
            ],
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        visibility = {"legend": False, "toggle_3d": True}
        mock_widget_map.set_map_control_visibility(visibility)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        visibility = {"legend": False, "toggle_3d": True}
        mock_widget_map.set_map_control_visibility(**visibility)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestGetSplitMode:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_split_mode()

        expected = {
            "type": "v1/map-sdk-get-split-mode",
            "args": [],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestSetSplitMode:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-set-split-mode",
            "args": [
                "swipe",
                {
                    "layers": [[LAYER_UUID], []],
                    "isViewSynced": True,
                    "isZoomSynced": True,
                },
            ],
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        options = {
            "layers": [[LAYER_UUID], []],
            "is_view_synced": True,
            "is_zoom_synced": True,
        }
        mock_widget_map.set_split_mode("swipe", options)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)

    def test_widget_message_kwargs(
        self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap
    ):
        options = {
            "layers": [[LAYER_UUID], []],
            "is_view_synced": True,
            "is_zoom_synced": True,
        }
        mock_widget_map.set_split_mode("swipe", **options)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestSetTheme:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.set_theme(preset="light", background_color="blue")

        expected = {
            "type": "v1/map-sdk-set-theme",
            "args": [{"preset": "light", "options": {"backgroundColor": "blue"}}],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestGetMapConfig:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_map_config()

        expected = {
            "type": "v1/map-sdk-get-map-config",
            "args": [],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestSetMapConfig:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        config = {"map": "config"}
        dataset = {"id": "dataset-id", "type": "local", "data": "dataset-data"}

        mock_widget_map.set_map_config(config, additional_datasets=[dataset])

        expected = {
            "type": "v1/map-sdk-set-map-config",
            "args": [
                {"map": "config"},
                {
                    "additionalDatasets": [
                        {"id": "dataset-id", "type": "local", "data": "dataset-data"}
                    ]
                },
            ],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestGetMapStyles:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_map_styles()

        expected = {
            "type": "v1/map-sdk-get-map-styles",
            "args": [],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)
