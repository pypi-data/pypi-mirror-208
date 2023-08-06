import abc
from typing import Callable, Dict, List, Optional, Sequence, Type, Union

from unfolded.map_sdk.api.base import Action
from unfolded.map_sdk.api.enums import EventType
from unfolded.map_sdk.types import (
    ErrorResponse,
    EventResponse,
    MessageResponse,
    ResponseClass,
)


class BaseTransport(abc.ABC):
    @abc.abstractmethod
    def send_action(
        self, *, action: Action, response_class: Optional[Type[ResponseClass]] = None
    ) -> Optional[ResponseClass]:
        pass

    @abc.abstractmethod
    def send_action_non_null(
        self, *, action: Action, response_class: Optional[Type[ResponseClass]] = None
    ) -> Optional[ResponseClass]:
        pass


class BaseInteractiveTransport(BaseTransport):
    # Note: this is stored as a dict instead of the EventHandlers model to avoid circular imports
    event_handlers: Dict[str, Callable]
    _has_loaded: bool

    @abc.abstractmethod
    def send_action_non_null(
        self,
        *,
        action: Action,
        response_class: Optional[Type[ResponseClass]] = None,
    ) -> ResponseClass:
        pass

    @abc.abstractmethod
    def receive_message(
        self,
        content: Union[EventResponse, MessageResponse, ErrorResponse],
        buffers: List[bytes],
    ) -> None:
        pass

    @abc.abstractmethod
    def set_event_handlers(self, event_handlers: Dict[str, Callable]) -> None:
        pass

    @abc.abstractmethod
    def remove_event_handlers(self, names: Sequence[Union[str, EventType]]) -> None:
        pass


class BaseNonInteractiveTransport(BaseTransport):
    @abc.abstractmethod
    def send_action(
        self, *, action: Action, response_class: Optional[Type[ResponseClass]] = None
    ) -> None:
        pass

    def send_action_non_null(
        self, *, action: Action, response_class: Optional[Type[ResponseClass]] = None
    ) -> None:
        self.send_action(action=action, response_class=response_class)
