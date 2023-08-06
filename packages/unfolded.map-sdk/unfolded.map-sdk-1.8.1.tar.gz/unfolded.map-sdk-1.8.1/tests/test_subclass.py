import inspect
import sys
from inspect import signature
from typing import Union

import pytest

from unfolded.map_sdk.api.dataset_api import (
    BaseDatasetApiMethods,
    DatasetApiInteractiveMixin,
    DatasetApiNonInteractiveMixin,
)
from unfolded.map_sdk.api.filter_api import (
    BaseFilterApiMethods,
    FilterApiInteractiveMixin,
    FilterApiNonInteractiveMixin,
)
from unfolded.map_sdk.api.layer_api import (
    BaseLayerApiMethods,
    LayerApiInteractiveMixin,
    LayerApiNonInteractiveMixin,
)
from unfolded.map_sdk.api.map_api import (
    BaseMapApiMethods,
    MapApiInteractiveMixin,
    MapApiNonInteractiveMixin,
)

if sys.version_info >= (3, 8):
    from typing import get_args, get_origin
else:
    from typing_extensions import get_args, get_origin

API_CLASSES = [
    [BaseMapApiMethods, MapApiInteractiveMixin, MapApiNonInteractiveMixin],
    [BaseDatasetApiMethods, DatasetApiInteractiveMixin, DatasetApiNonInteractiveMixin],
    [BaseLayerApiMethods, LayerApiInteractiveMixin, LayerApiNonInteractiveMixin],
    [BaseFilterApiMethods, FilterApiInteractiveMixin, FilterApiNonInteractiveMixin],
]


class TestSubclass:
    """Tests relating to Map SDK API subclasses.
    Specifically, whether interactive and non-interactive mixins
    have the right type signatures on their methods
    """

    @pytest.mark.parametrize("base,interactive,non_interactive", API_CLASSES)
    def test_subclasses(self, base, interactive, non_interactive):

        base_methods = inspect.getmembers(base, predicate=inspect.isfunction)
        interactive_methods = dict(
            inspect.getmembers(interactive, predicate=inspect.isfunction)
        )
        non_interactive_methods = dict(
            inspect.getmembers(non_interactive, predicate=inspect.isfunction)
        )

        for func_name, func in base_methods:
            sig = signature(func)
            base_return_type = sig.return_annotation
            # Match Optional return type
            if get_origin(base_return_type) is Union and get_args(base_return_type)[
                -1
            ] is type(None):

                *declared_return_type, _ = get_args(base_return_type)

                sub_return_type = signature(
                    interactive_methods[func_name]
                ).return_annotation

                # Check if subclass return type is Union
                if get_origin(sub_return_type) is Union:
                    sub_return_type = list(get_args(sub_return_type))
                # Otherwise we should only have one non-None type in the Union
                else:
                    assert (
                        len(declared_return_type) == 1
                    ), f"{func_name} in {base.__name__} has too many non-None return types: {declared_return_type}, {func_name} in {interactive.__name__} should return a Union"
                    declared_return_type = declared_return_type[0]

                # Make sure method is subclassed properly
                assert (
                    sub_return_type == declared_return_type
                ), f"{func_name} in {interactive.__name__} has wrong return type"
                assert (
                    signature(non_interactive_methods[func_name]).return_annotation
                    is None
                ), f"{func_name} in {non_interactive.__name__} has non-None return type"

            # match None return type
            elif base_return_type is None:
                if func_name in interactive_methods:
                    sub_func = interactive_methods[func_name]
                    # Check if subclass redefines function
                    assert (
                        sub_func.__qualname__ == func.__qualname__
                    ), f"{func_name} does not need to appear in {interactive.__name__} since return type is None"
                if func_name in non_interactive_methods:
                    sub_func = non_interactive_methods[func_name]
                    # Check if subclass redefines function
                    assert (
                        sub_func.__qualname__ == func.__qualname__
                    ), f"{func_name} does not need to appear in {non_interactive.__name__} since return type is None"
            else:
                raise TypeError(
                    f"{func_name} in {base.__name__} has non-Optional, non-None return type"
                )
