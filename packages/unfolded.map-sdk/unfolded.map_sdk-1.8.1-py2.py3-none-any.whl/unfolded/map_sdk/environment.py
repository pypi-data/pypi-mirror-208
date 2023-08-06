"""Helpers to deduce what type of Python environment is currently being used
"""

import os
from enum import Enum
from typing import Union

import IPython

__all__ = ("Environment", "CURRENT_ENVIRONMENT", "default_height")


class Environment(str, Enum):
    AZURE = "azure"
    COCALC = "cocalc"
    COLAB = "colab"
    CONSOLE = "console"
    DATABRICKS = "databricks"
    JUPYTER_LAB = "jupyterlab"
    JUPYTER_NOTEBOOK = "notebook"
    KAGGLE = "kaggle"
    NTERACT = "nteract"
    VSCODE = "vscode"


def deduce_current_environment() -> Environment:
    """Deduce current Python environment"""
    # Ported from Plotly under the MIT license:
    # https://github.com/plotly/plotly.py/blob/2c2dd6ab2eeff73c782457f33c590c1d09a97625/packages/python/plotly/plotly/io/_renderers.py#L455-L536

    if IPython and IPython.get_ipython():
        # Try to detect environment so that we can enable a useful
        # default renderer
        try:
            import google.colab  # pylint:disable=import-outside-toplevel,unused-import

            return Environment.COLAB
        except ImportError:
            pass

        # Check if we're running in a Kaggle notebook
        if os.path.exists("/kaggle/input"):
            return Environment.KAGGLE

        # Check if we're running in an Azure Notebook
        if "AZURE_NOTEBOOKS_HOST" in os.environ:
            return Environment.AZURE

        # Check if we're running in VSCode
        if "VSCODE_PID" in os.environ:
            return Environment.VSCODE

        # Check if we're running in nteract
        if "NTERACT_EXE" in os.environ:
            return Environment.NTERACT

        # Check if we're running in CoCalc
        if "COCALC_PROJECT_ID" in os.environ:
            return Environment.COCALC

        if "DATABRICKS_RUNTIME_VERSION" in os.environ:
            return Environment.DATABRICKS

        # Check if we're running in IPython terminal
        if IPython.get_ipython().__class__.__name__ == "TerminalInteractiveShell":
            return Environment.CONSOLE

    # Fall back to console environment
    return Environment.CONSOLE


CURRENT_ENVIRONMENT = deduce_current_environment()


def default_height() -> Union[str, int]:
    """Provide default widget heights for current environment"""
    height: Union[str, int] = "100%"

    if CURRENT_ENVIRONMENT in [
        Environment.COLAB,
        Environment.VSCODE,
        Environment.DATABRICKS,
    ]:
        # Colab: 100% height shows up as very small
        # VSCode: 100% height shows up as very small
        # Databricks: 100% height leads to the iframe height
        # growing infinitely in Databricks due to their resizing logic
        height = 500

    return height
