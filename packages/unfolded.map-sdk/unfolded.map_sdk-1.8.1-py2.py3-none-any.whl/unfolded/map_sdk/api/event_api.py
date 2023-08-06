from abc import abstractmethod
from typing import Any, List, Sequence, Union

from unfolded.map_sdk.api.base import Action
from unfolded.map_sdk.api.enums import EVENT_HANDLER_MAP, ActionType, EventType
from unfolded.map_sdk.api.filter_api import FilterEventHandlers
from unfolded.map_sdk.api.layer_api import LayerEventHandlers
from unfolded.map_sdk.api.map_api import MapEventHandlers
from unfolded.map_sdk.transport.base import BaseInteractiveTransport
from unfolded.map_sdk.utils.validators import validate_kwargs


class EventHandlers(MapEventHandlers, FilterEventHandlers, LayerEventHandlers):
    ...


###########
# ACTIONS #
###########


class SetEventHandlers(Action):
    class Meta(Action.Meta):
        args = ["names"]

    type: ActionType = ActionType.SET_EVENT_HANDLERS
    names: List[EventType]


class RemoveEventHandlers(Action):
    class Meta(Action.Meta):
        args = ["names"]

    type: ActionType = ActionType.REMOVE_EVENT_HANDLERS
    names: List[EventType]


###########
# METHODS #
###########


class BaseEventApiMethods:
    @abstractmethod
    def set_event_handlers(
        self, event_handlers: Union[dict, EventHandlers, None], **kwargs: Any
    ) -> None:
        ...

    @abstractmethod
    def remove_event_handlers(
        self, event_handlers: Sequence[Union[str, EventType]]
    ) -> None:
        ...


# The Event API is not implemented for the pure HTML static map because the static HTML bundle can't
# send events back to Python
class EventApiInteractiveMixin(BaseEventApiMethods):
    transport: BaseInteractiveTransport

    @validate_kwargs(positional_only=["event_handlers"])
    def set_event_handlers(
        self, event_handlers: Union[dict, EventHandlers, None] = None, **kwargs: Any
    ) -> None:
        if not isinstance(event_handlers, EventHandlers):
            event_handlers = (
                EventHandlers(**event_handlers)
                if event_handlers is not None
                else EventHandlers(**kwargs)
            )

        attribute_names = event_handlers.dict(exclude_none=True).keys()
        event_values: List[EventType] = []
        for attr_name in attribute_names:
            event_val = EVENT_HANDLER_MAP.get(attr_name)
            if event_val:
                event_values.append(event_val)

        action = SetEventHandlers(names=event_values)
        self.transport.send_action(action=action)

        self.transport.set_event_handlers(event_handlers.dict(exclude_none=True))

    def remove_event_handlers(
        self, event_handlers: Sequence[Union[str, EventType]]
    ) -> None:
        action = RemoveEventHandlers(names=event_handlers)
        self.transport.send_action(action=action)

        self.transport.remove_event_handlers(event_handlers)
