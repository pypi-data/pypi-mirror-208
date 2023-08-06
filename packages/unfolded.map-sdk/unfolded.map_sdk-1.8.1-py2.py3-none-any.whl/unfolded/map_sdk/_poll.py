"""Vendored jupyter-ui-poll version 0.1.3 under the MIT license

We use jupyter-ui-poll to offer synchronous messaging between Python and JS. As of November 2021,
Colab uses an older ipykernel version 4.x. Version 0.1.3 of jupyter-ui-poll supported ipykernel 4.x
but newer versions support only ipykernel 5.x and 6.x. In
https://github.com/Kirill888/jupyter-ui-poll/issues/18 the author was reluctant to support ipykernel
4.x going forward. To solve this, we vendor here version 0.1.3 of jupyter-ui-poll, then can switch
between polling implementation depending on the version of ipykernel.
"""
import asyncio
import sys
import time
from contextlib import contextmanager
from typing import Any, Callable, Iterable, Iterator
from warnings import warn

from IPython import get_ipython
from IPython.core.interactiveshell import InteractiveShell

__all__ = (
    "ui_events",
    "with_ui_events",
    "run_ui_poll_loop",
)


def _replay_events(shell: InteractiveShell, events: Iterable[Iterable]) -> None:
    kernel = shell.kernel  # type: ignore
    sys.stdout.flush()
    sys.stderr.flush()
    for stream, ident, parent in events:
        kernel.set_parent(ident, parent)
        # kernel._aborting does not exist on ipykernel 4
        if hasattr(kernel, "_aborting") and kernel._aborting:
            kernel._send_abort_reply(stream, parent, ident)
        else:
            kernel.execute_request(stream, ident, parent)


@contextmanager
def ui_events() -> Iterator[Callable]:
    """
    Gives you a function you can call to process ui events while running a long
    task inside a Jupyter cell.

    .. code-block: python
       with ui_events() as ui_poll:
          while some_condition:
             ui_poll(10)  # Process upto 10 UI events if any happened
             do_some_more_compute()


    - Delay processing `execute_request` IPython kernel events
    - Calls `kernel.do_one_iteration()`
    - Schedule replay of any blocked `execute_request` events upon
      exiting from the context manager
    """

    shell = get_ipython()
    kernel = shell.kernel
    events = []
    kernel.shell_handlers["execute_request"] = lambda *e: events.append(e)
    current_parent = (kernel._parent_ident, kernel._parent_header)

    def poll(n: int = 1) -> None:
        for _ in range(n):
            # ensure stdout still happens in the same cell
            kernel.set_parent(*current_parent)
            kernel.do_one_iteration()
            kernel.set_parent(*current_parent)

    try:
        poll()  # ensure poll is called at least once to correct output redirect
        yield poll
    finally:
        kernel.shell_handlers["execute_request"] = kernel.execute_request
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.call_soon(lambda: _replay_events(shell, events))
        else:
            warn(
                "Automatic execution of scheduled cells only works with asyncio based ipython"
            )


def with_ui_events(its: Iterator, n: int = 1) -> Iterator:
    """
    Deal with kernel ui events while processing a long sequence

    :param its: Iterator to pass through
    :param n:   Number of events to process in between items

    - Delay processing `execute_request` IPython kernel events
    - Inject calls to `kernel.do_one_iteration()` in between iterations
    - Schedule replay of any blocked `execute_request` events when data sequence is exhausted
    """
    with ui_events() as poll:
        try:
            for x in its:
                poll(n)
                yield x
        except GeneratorExit:
            pass
        except Exception as e:
            raise e


def run_ui_poll_loop(f: Callable, sleep: float = 0.02, n: int = 1) -> Any:
    """
    Repeatedly call `f()` until it returns non-None value while also responding to widget events.

    This blocks execution of cells below in the notebook while still preserving
    interactivity of jupyter widgets.

    :param f: Function to periodically call (`f()` should not block for long)
    :param sleep: Amount of time to sleep in between polling (in seconds, 1/50 is the default)
    :param n: Number of events to process per iteration

    Returns
    =======
    First non-None value returned from `f()`
    """

    def as_iterator(f: Callable, sleep: float) -> Iterator:
        x = None
        while x is None:
            if sleep is not None:
                time.sleep(sleep)

            x = f()
            yield x

    for x in with_ui_events(as_iterator(f, sleep), n):
        if x is not None:
            return x
