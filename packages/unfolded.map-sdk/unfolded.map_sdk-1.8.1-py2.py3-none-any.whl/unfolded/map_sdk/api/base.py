from typing import Callable, List, Tuple, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, StrictFloat, StrictInt

from unfolded.map_sdk.api.enums import ActionType

Number = Union[StrictFloat, StrictInt]
Range = Tuple[Number, Number]
TimeRange = Tuple[Number, Number]


class ApiBaseModel(BaseModel):
    class Config:
        validate_assignment = True
        extra = "forbid"


class CamelCaseBaseModel(ApiBaseModel):
    class Config:
        allow_population_by_field_name = True

        @staticmethod
        def to_camel_case(snake_str: str) -> str:
            """Convert snake_case string to camelCase
            https://stackoverflow.com/a/19053800
            """
            components = snake_str.split("_")
            # We capitalize the first letter of each component except the first one
            # with the 'title' method and join them together.
            return components[0] + "".join(x.title() for x in components[1:])

        alias_generator = to_camel_case


class KebabCaseBaseModel(ApiBaseModel):
    class Config:
        allow_population_by_field_name = True
        alias_generator: Callable[[str], str] = lambda snake_str: snake_str.replace(
            "_", "-"
        )


class Action(CamelCaseBaseModel):
    """Base Action payload class"""

    class Meta:
        args: List[str] = []
        """Order in which arguments should be serialized"""

        options: List[str] = []
        """Fields to be collected into an options dict/object."""

    type: ActionType
    message_id: UUID = Field(default_factory=uuid4)
