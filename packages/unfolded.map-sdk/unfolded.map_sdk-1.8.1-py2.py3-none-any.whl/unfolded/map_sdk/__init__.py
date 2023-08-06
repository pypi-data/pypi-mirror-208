from typing import Dict, List

from unfolded.map_sdk._version import __version__
from unfolded.map_sdk.api.create_map import create_map
from unfolded.map_sdk.colab import enable_colab_custom_widgets

enable_colab_custom_widgets()


def _jupyter_labextension_paths() -> List[Dict[str, str]]:
    """Called by Jupyter Lab Server to detect if it is a valid labextension and
    to install the widget
    Returns
    =======
    src: Source directory name to copy files from. Webpack outputs generated files
        into this directory and Jupyter Lab copies from this directory during
        widget installation
    dest: Destination directory name to install widget files to. Jupyter Lab copies
        from `src` directory into <jupyter path>/labextensions/<dest> directory
        during widget installation
    """
    return [{"src": "labextension", "dest": "@unfolded/jupyter-map-sdk"}]


def _jupyter_nbextension_paths() -> List[Dict[str, str]]:
    """Called by Jupyter Notebook Server to detect if it is a valid nbextension and
    to install the widget
    Returns
    =======
    section: The section of the Jupyter Notebook Server to change.
        Must be 'notebook' for widget extensions
    src: Source directory name to copy files from. Webpack outputs generated files
        into this directory and Jupyter Notebook copies from this directory during
        widget installation
    dest: Destination directory name to install widget files to. Jupyter Notebook copies
        from `src` directory into <jupyter path>/nbextensions/<dest> directory
        during widget installation
    require: Path to importable AMD Javascript module inside the
        <jupyter path>/nbextensions/<dest> directory
    """
    return [
        {
            "section": "notebook",
            "src": "nbextension",
            "dest": "unfolded/map_sdk",
            "require": "unfolded/map_sdk/extension",
        }
    ]
