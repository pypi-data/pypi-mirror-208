def test_nbextension_path() -> None:
    # Check that magic function can be imported from package root:
    # pylint:disable=import-outside-toplevel
    from unfolded.map_sdk import _jupyter_nbextension_paths

    # Ensure that it can be called without incident:
    path = _jupyter_nbextension_paths()
    # Some sanity checks:
    assert len(path) == 1
    assert isinstance(path[0], dict)
