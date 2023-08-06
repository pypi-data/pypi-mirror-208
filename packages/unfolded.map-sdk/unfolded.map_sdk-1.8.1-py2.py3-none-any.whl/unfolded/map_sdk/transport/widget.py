import sys
from concurrent.futures import Future
from time import time
from typing import Callable, Dict, List, Optional, Sequence, Type, Union, overload

from ipywidgets import DOMWidget
from pydantic import parse_obj_as

from unfolded.map_sdk.api.base import Action
from unfolded.map_sdk.api.enums import (
    REVERSE_EVENT_HANDLER_MAP,
    EventType,
    is_event_type,
)
from unfolded.map_sdk.api.event_api import EventHandlers
from unfolded.map_sdk.errors import MapSDKException, UnfoldedStudioException
from unfolded.map_sdk.poll import run_ui_poll_loop
from unfolded.map_sdk.transport.base import BaseInteractiveTransport
from unfolded.map_sdk.types import (
    ErrorResponse,
    EventResponse,
    MessageResponse,
    ResponseClass,
    StoredFuture,
    WidgetMessage,
)
from unfolded.map_sdk.utils.serialization import serialize_action

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class BaseWidgetTransport(BaseInteractiveTransport):
    widget: DOMWidget
    futures: Dict[str, StoredFuture]
    event_handlers: Dict[str, Callable]

    def __init__(
        self,
        widget: DOMWidget,
    ) -> None:
        super().__init__()
        self.widget = widget
        self.futures: Dict[str, StoredFuture] = {}
        self.event_handlers = {}
        self._has_loaded = False

    def set_event_handlers(self, event_handlers: Dict[str, Callable]) -> None:
        self.event_handlers = EventHandlers(
            **{**self.event_handlers, **event_handlers}
        ).dict(exclude_none=True)

    def remove_event_handlers(self, names: Sequence[Union[str, EventType]]) -> None:
        for name in names:
            setattr(self.event_handlers, name, None)

    def _send_widget_message(
        self, content: Union[WidgetMessage, Dict], buffers: Optional[List[bytes]]
    ) -> None:
        """Send message to JS using Jupyter Widgets' messaging protocol"""
        self.widget.send(content=content, buffers=buffers)

    def receive_message(
        self,
        content: Union[EventResponse, MessageResponse, ErrorResponse],
        buffers: Optional[List[bytes]] = None,
    ) -> None:
        """Receive message from JS"""

        if content["type"] == "event":
            self.receive_message_event(content, buffers=buffers)

        elif content["type"] == "error":
            self.receive_message_error(content, buffers=buffers)

        elif content["type"] == "response":
            self.receive_message_valid(content, buffers=buffers)

    def receive_message_event(
        self, content: EventResponse, buffers: Optional[List[bytes]] = None
    ) -> None:
        # pylint: disable=unused-argument
        """Receive event notification from JS"""
        event_type = content.get("eventType")

        if not event_type or not is_event_type(event_type):
            raise MapSDKException(f"{event_type} is not a supported event type")

        event_type = EventType(event_type)
        event_name = REVERSE_EVENT_HANDLER_MAP.get(event_type)
        if event_name == "on_load":
            self._has_loaded = True
        elif event_name:
            callback = self.event_handlers.get(event_name)
            data = content.get("data")

            if callback and data is not None:
                callback(data)

    def receive_message_error(
        self, content: ErrorResponse, buffers: Optional[List[bytes]] = None
    ) -> None:
        # pylint: disable=unused-argument
        """Receive error response message from JS"""
        message_id = content.get("messageId")
        error = content.get("error")

        if not message_id or message_id not in self.futures:
            return

        future_ref = self.futures.pop(message_id)
        future_ref.future.set_exception(UnfoldedStudioException(error))

    def receive_message_valid(
        self, content: MessageResponse, buffers: Optional[List[bytes]] = None
    ) -> None:
        # pylint: disable=unused-argument
        """Receive response message from JS"""
        message_id = content.get("messageId")
        data = content.get("data")

        if not message_id or message_id not in self.futures:
            return

        future_ref = self.futures.pop(message_id)
        response_class = future_ref.response_class

        if response_class is not None:
            try:
                # parse_obj_as should work with any arbitrary pydantic-compatible
                # types
                # https://pydantic-docs.helpmanual.io/usage/models/#parsing-data-into-a-specified-type
                parsed = parse_obj_as(response_class, data)
                future_ref.future.set_result(parsed)
                return
            except Exception as e:
                future_ref.future.set_exception(e)

        future_ref.future.set_result(data)


class BlockingWidgetTransport(BaseWidgetTransport):
    def send_action(
        self,
        *,
        action: Action,
        response_class: Optional[Type[ResponseClass]] = None,
    ) -> Optional[ResponseClass]:
        if not self._has_loaded:
            raise MapSDKException("Cannot call map method before rendering map.")

        content, buffers = serialize_action(action)
        self._send_widget_message(content, buffers)

        future: "Future[ResponseClass]" = Future()
        stored_future: StoredFuture[Type[ResponseClass]] = StoredFuture(
            future=future, response_class=response_class
        )
        self.futures[str(action.message_id)] = stored_future

        result = self._wait_for_future(future, response_optional=True)
        if isinstance(result, Exception):
            raise result

        return result

    def send_action_non_null(
        self,
        *,
        action: Action,
        response_class: Optional[Type[ResponseClass]] = None,
    ) -> ResponseClass:
        if not self._has_loaded:
            raise MapSDKException("Cannot call map method before rendering map.")

        content, buffers = serialize_action(action)
        self._send_widget_message(content, buffers)

        future: "Future[ResponseClass]" = Future()
        stored_future: StoredFuture[Type[ResponseClass]] = StoredFuture(
            future=future, response_class=response_class
        )
        self.futures[str(action.message_id)] = stored_future

        result = self._wait_for_future(future, response_optional=False)
        if isinstance(result, Exception):
            raise result

        return result

    @overload
    def _wait_for_future(
        self,
        future: "Future[ResponseClass]",
        response_optional: Literal[True],
        timeout: float = 5,
    ) -> Optional[ResponseClass]:
        ...

    @overload
    def _wait_for_future(
        self,
        future: "Future[ResponseClass]",
        response_optional: Literal[False],
        timeout: float = 5,
    ) -> ResponseClass:
        ...

    def _wait_for_future(
        self,
        future: "Future[ResponseClass]",
        response_optional: bool,
        timeout: float = 5,
    ) -> Optional[ResponseClass]:
        """Wait in a blocking way for future to be completed

        Args:
            future: Future object to wait on
            response_optional: if True, the response type can be `None`. Otherwise, a `None`
                response from JS will be raised as an exception.
            timeout: Timeout period in seconds after which polling will finish

        Returns:
            Result of future object (could be `None` if response_optional is True). Can also return an Exception stored within the future.
        """
        start_time = time()
        sentinel_object = object()

        def poll_callback():
            """Callback to be run in run_ui_poll_loop

            Polls for completion of future up to specified timeout
            """
            if future.done():
                # Checking for `.exception()` prevents raising the exception here, which would
                # happen if we called `.result()` and an exception had been set
                if future.exception():
                    return future.exception()

                # Returning None from the callback will not break out of the polling
                if future.result() is None:
                    if response_optional:
                        return sentinel_object
                    else:
                        return UnfoldedStudioException(
                            "Got unexpected None response from widget"
                        )

                return future.result()

            if time() - start_time > timeout:
                return UnfoldedStudioException("Timeout waiting for widget response")

            return None

        poll_response = run_ui_poll_loop(poll_callback, sleep=1 / 10, n=4)

        if poll_response is sentinel_object:
            return None

        return poll_response
