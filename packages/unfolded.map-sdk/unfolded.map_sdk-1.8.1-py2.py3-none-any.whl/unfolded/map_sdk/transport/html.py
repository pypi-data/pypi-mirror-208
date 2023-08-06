import json
from typing import List, Optional, Type
from uuid import uuid4

from jinja2 import Environment, PackageLoader

from unfolded.map_sdk._version import __version__
from unfolded.map_sdk.api.base import Action
from unfolded.map_sdk.transport.base import BaseNonInteractiveTransport
from unfolded.map_sdk.types import ResponseClass
from unfolded.map_sdk.utils.serialization import serialize_action


class HTMLTransport(BaseNonInteractiveTransport):
    """Transport used in a static HTML map"""

    action_list: List[Action]

    def __init__(self) -> None:
        super().__init__()
        self.action_list = []

    def send_action(
        self,
        *,
        action: Action,
        response_class: Optional[Type[ResponseClass]] = None,
    ) -> None:
        # pylint:disable=unused-argument
        self.action_list.append(action)

    @property
    def serialized_actions(self):
        return [
            serialize_action(action, renderer="html")[0] for action in self.action_list
        ]

    def render_template(self, **kwargs) -> str:
        self.rendered = True
        j2_env = Environment(
            loader=PackageLoader("unfolded.map_sdk"),
            autoescape=True,
            trim_blocks=True,
            keep_trailing_newline=True,
        )
        template = j2_env.get_template("html_map_sdk.j2")

        constructor_args = {key: json.dumps(val) for key, val in kwargs.items()}

        html_str = template.render(
            version=__version__,
            # We need to escape newlines again since the templating removes a backslash.
            # Since we control self.serialized actions, the only newlines will come from
            # pd.to_csv() or other user-provided input, which will be inside a string
            actions=json.dumps(self.serialized_actions).replace(r"\n", r"\\n"),
            div_id=uuid4(),
            **constructor_args,
        )
        return html_str
