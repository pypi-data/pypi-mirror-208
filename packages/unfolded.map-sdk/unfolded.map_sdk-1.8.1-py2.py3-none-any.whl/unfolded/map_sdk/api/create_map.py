import sys
from typing import Any, Union, overload

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from unfolded.map_sdk.environment import CURRENT_ENVIRONMENT, Environment
from unfolded.map_sdk.errors import MapSDKException
from unfolded.map_sdk.map import HTMLMap, SyncWidgetMap

__all__ = ("create_map",)

DATABRICKS_HTML_MAP_MSG = """Databricks environment detected, using HTML renderer.
SDK function calls after a map is rendered will not update the map automatically,
the map must be re-rendered to update.
To hide this warning in the future, pass `renderer="html"`.
"""

# Note: not possible (I think) to have this typing overload understand when the current environment
# is databricks
@overload
def create_map(*, renderer: Literal["html"], **kwargs: Any) -> HTMLMap:
    ...


@overload
def create_map(
    *, renderer: Literal["widget", None] = None, **kwargs: Any
) -> SyncWidgetMap:
    ...


def create_map(
    *, renderer: Literal["html", "widget", None] = None, **kwargs: Any
) -> Union[HTMLMap, SyncWidgetMap]:
    """Create an unfolded map

    Args:
        renderer (str): Which renderer to use for the map, either "html" or "widget".
                        Default: "widget" if supported by your environment.
    """
    if CURRENT_ENVIRONMENT == Environment.DATABRICKS:
        if renderer == "widget":
            raise MapSDKException(
                "Cannot use widget renderer in Databricks environment"
            )
        elif renderer is None:
            sys.stderr.write(DATABRICKS_HTML_MAP_MSG)
        return HTMLMap(**kwargs)
    elif renderer == "html":
        return HTMLMap(**kwargs)
    else:
        return SyncWidgetMap(**kwargs)
