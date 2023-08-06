# pylint:disable=redefined-outer-name

import json
import sys
from pathlib import Path
from typing import List, Optional, Union, cast

import pytest
from ipykernel.comm import Comm
from ipywidgets import Widget
from pytest_mock import MockerFixture
from traitlets import Unicode

from unfolded.map_sdk.map.widget import SyncWidgetMap
from unfolded.map_sdk.types import WidgetMessage

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict

HERE = Path(__file__).parent


class CommMessageDataUpdate(TypedDict):
    method: Literal["update"]
    state: dict
    buffer_paths: list


class CommMessageDataCustom(TypedDict):
    method: Literal["custom"]
    content: WidgetMessage


class CommMessage(TypedDict):
    data: Union[CommMessageDataCustom, CommMessageDataUpdate]
    buffers: Optional[list]


class MockComm(Comm):
    """A mock Comm object.

    Can be used to inspect calls to Comm's open/send/close methods.
    """

    comm_id = Unicode("a-b-c-d")
    kernel = "ipykernel.kernelbase.Kernel"  # type: ignore

    log_open: List[tuple]
    log_send: List[CommMessage]
    log_close: List[tuple]

    def __init__(self, *args, **kwargs):
        self.log_open = []
        self.log_send = []
        self.log_close = []
        super().__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        self.log_open.append((args, kwargs))

    def send(self, *args, **kwargs):
        if args:
            raise ValueError("only kwargs expected in send comm method")

        self.log_send.append(cast(CommMessage, kwargs))

    def close(self, *args, **kwargs):
        self.log_close.append((args, kwargs))

    # TODO: try to figure out how to mock comm _responses_
    # def handle_msg(self, msg):
    #     """Handle a comm_msg message"""
    #     if self._msg_callback:
    #         self._msg_callback(msg)


@pytest.fixture
def mock_comm(mock_wait_for_future):  # pylint:disable=unused-argument
    _widget_attrs = {}
    undefined = object()

    # Create a single instance of the mocked comm to set as the comm for mock_widget_map
    # and to return from this function to check comm calls
    mock_comm_instance = MockComm()

    _widget_attrs["_ipython_display_"] = Widget._ipython_display_

    def raise_not_implemented(*args, **kwargs):
        raise NotImplementedError()

    Widget._ipython_display_ = raise_not_implemented

    yield mock_comm_instance

    for attr, value in _widget_attrs.items():
        if value is undefined:
            delattr(Widget, attr)
        else:
            setattr(Widget, attr, value)


@pytest.fixture
def mock_wait_for_future(mocker: MockerFixture):
    mocker.patch(
        "unfolded.map_sdk.transport.widget.BlockingWidgetTransport._wait_for_future"
    )


@pytest.fixture
def mock_widget_map(mock_comm: MockComm) -> SyncWidgetMap:
    m = SyncWidgetMap()
    # set mock_comm as the comm for the map
    m.comm = mock_comm
    m.transport._has_loaded = True
    return m


@pytest.fixture
def sentinel2_stac_item():
    path = HERE / "fixtures" / "raster" / "item" / "sentinel-2-l2a.json"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def sentinel2_stac_collection():
    path = HERE / "fixtures" / "raster" / "collection" / "sentinel-s2-l2a-cogs.json"
    with open(path) as f:
        return json.load(f)
