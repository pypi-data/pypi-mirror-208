import sys


def enable_colab_custom_widgets() -> None:
    """Enable custom widget support in Colab"""
    # Uses same approach as ipyleaflet
    # https://github.com/jupyter-widgets/ipyleaflet/pull/871
    if "google.colab" in sys.modules:
        from google.colab import output  # pylint:disable=import-outside-toplevel

        output.enable_custom_widget_manager()
