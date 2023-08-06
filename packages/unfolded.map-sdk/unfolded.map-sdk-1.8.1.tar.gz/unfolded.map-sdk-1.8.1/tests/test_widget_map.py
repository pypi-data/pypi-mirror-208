import pytest

from tests.conftest import MockComm
from unfolded.map_sdk.errors import MapSDKException
from unfolded.map_sdk.map.widget import SyncWidgetMap


class TestWidgetTransport:
    def test_event_handler_merge(self):

        m = SyncWidgetMap()
        transport = m.transport

        func1 = lambda view: print(1)
        func2 = lambda mouse_event: print(2)
        func3 = lambda view: print(3)
        func4 = lambda filter: print(4)

        event_handlers_1 = {"on_view_update": func1, "on_click": func2}

        transport.set_event_handlers(event_handlers_1)
        assert transport.event_handlers == event_handlers_1

        event_handlers_2 = {"on_view_update": func3, "on_filter_update": func4}

        transport.set_event_handlers(event_handlers_2)

        event_handlers_final = {
            "on_view_update": func3,
            "on_click": func2,
            "on_filter_update": func4,
        }
        assert transport.event_handlers == event_handlers_final

    def test_calling_method_before_rendering_raises(
        self, mock_comm: MockComm  # pylint:disable=unused-argument
    ):
        m = SyncWidgetMap()
        with pytest.raises(MapSDKException):
            m.set_view(longitude=0)
