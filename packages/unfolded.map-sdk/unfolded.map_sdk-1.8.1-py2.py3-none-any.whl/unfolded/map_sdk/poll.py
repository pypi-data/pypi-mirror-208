from typing import Callable

import ipykernel

from unfolded.map_sdk._poll import run_ui_poll_loop as run_ui_poll_loop_v4
from unfolded.map_sdk._poll_v56 import run_ui_poll_loop as run_ui_poll_loop_v56

__all__ = "run_ui_poll_loop"


def get_polling_fn() -> Callable:
    """Return valid implementation of jupyter-ui-poll for ipykernel version

    Returns:
        Callable: implementation of run_ui_poll_loop for this ipykernel version
    """
    ipykernel_major_version = int(ipykernel.__version__[0])

    if ipykernel_major_version < 5:
        # NOTE: haven't tested this function on ipykernel v3 and prior
        return run_ui_poll_loop_v4
    else:
        return run_ui_poll_loop_v56


run_ui_poll_loop = get_polling_fn()
