from unittest.mock import patch

from unfolded.map_sdk.map.html import HTMLMap

from .fixtures.test_data import EARTHQUAKES_DF, EARTHQUAKES_GDF


# NOTE: if copy-pasting these snapshots into JupyterLab or Databricks to manually test
# with `IPython.display.HTML`, **you need to paste as a raw-string**. This means pasting
# as
# r"""
# <iframe>....
# """
# If you paste without the `r` prefix you'll get newline errors with csvs
class TestHTMLMap:
    @patch("unfolded.map_sdk.transport.html.__version__", "latest")
    @patch("unfolded.map_sdk.transport.html.uuid4", lambda: "test-div")
    def test_template_rendering(self, snapshot):

        m = HTMLMap()
        m.add_dataset(data=EARTHQUAKES_DF, label="Earthquakes")
        m.add_dataset(data=EARTHQUAKES_GDF, label="More Earthquakes")
        m.set_view(zoom=7)
        snapshot.assert_match(m._repr_html_(), "map.html")

    @patch("unfolded.map_sdk.transport.html.__version__", "latest")
    @patch("unfolded.map_sdk.transport.html.uuid4", lambda: "test-div")
    def test_iframe_template_rendering(self, snapshot):

        m = HTMLMap(iframe=True, style={"height": 500})
        m.add_dataset(data=EARTHQUAKES_DF, label="Earthquakes")
        m.add_dataset(data=EARTHQUAKES_GDF, label="More Earthquakes")
        m.set_view(zoom=7)
        snapshot.assert_match(m._repr_html_(), "iframe_map.html")

    def test_html_map_action_list(self):

        m = HTMLMap()
        transport = m.transport

        m.set_view(zoom=7)
        m.set_view_limits(min_zoom=5)

        assert transport.serialized_actions == [
            {"args": [{"zoom": 7}], "options": {"index": 0}, "funcName": "setView"},
            {
                "args": [{"minZoom": 5}],
                "options": {"index": 0},
                "funcName": "setViewLimits",
            },
        ]

        m.set_theme(preset="light")

        # action_list remembers all previous actions
        assert transport.serialized_actions == [
            {"args": [{"zoom": 7}], "options": {"index": 0}, "funcName": "setView"},
            {
                "args": [{"minZoom": 5}],
                "options": {"index": 0},
                "funcName": "setViewLimits",
            },
            {"args": [{"preset": "light", "options": {}}], "funcName": "setUiTheme"},
        ]
