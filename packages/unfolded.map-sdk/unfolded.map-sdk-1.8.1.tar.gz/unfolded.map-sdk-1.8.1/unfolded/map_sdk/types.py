import sys
from concurrent.futures import Future
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from unfolded.map_sdk.api.enums import ActionType, EventType

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict

ResponseClass = TypeVar("ResponseClass")

SDKArg = Union[str, int, float, dict]


class WidgetMessage(TypedDict):
    """Shape of message sent from Python to JS"""

    type: ActionType
    messageId: str
    args: List[SDKArg]
    options: Optional[Dict[str, SDKArg]]


class StoredFuture(Generic[ResponseClass]):
    """Shape of object stored in UnfoldedMap.futures"""

    future: Future
    response_class: Optional[ResponseClass]

    def __init__(self, future: Future, response_class: Optional[ResponseClass]) -> None:
        self.future = future
        self.response_class = response_class


# Use total=False to mark keys as optional
class EventResponse(TypedDict, total=False):
    """Shape of object returned for event handling"""

    type: Literal["event"]
    eventType: EventType
    data: Any


class MessageResponse(TypedDict, total=False):
    """Shape of object returned for messages"""

    type: Literal["response"]
    messageId: str
    data: Any


class ErrorResponse(TypedDict):
    """Shape of returned errors"""

    type: Literal["error"]
    messageId: str
    error: str
