# test_validate_kwargs_default
from typing import Union

import pytest

from unfolded.map_sdk.api.dataset_api import DatasetApiInteractiveMixin
from unfolded.map_sdk.errors import MapSDKException
from unfolded.map_sdk.utils.validators import validate_kwargs

from ..mocks.transport import MockInteractiveTransport


class TestValidateKwargs:
    def test_one_arg(self):

        # Default params: positional_only=None
        # pylint:disable=unused-argument
        @validate_kwargs()
        def _one_arg(foo: int, **kwargs):
            pass

        # Assert not raised as a positional arg
        _one_arg(0)

        # Assert not raised as a keyword arg
        _one_arg(foo=0)

        # Should raise with both a positional arg and a kwarg
        with pytest.raises(MapSDKException):
            _one_arg(0, kwarg="bar")

    def test_one_arg_with_default(self):
        # Default params: positional_only=None
        # pylint:disable=unused-argument
        @validate_kwargs()
        def _one_arg_with_default(foo: int = 1, **kwargs):
            pass

        # Assert not raised with no args
        # Note(Kyle): The default arg of the function is provided _after_ leaving the decorator, so
        # a default arg implies an empty `args` list.
        _one_arg_with_default()

        # Assert not raised as a positional arg
        _one_arg_with_default(0)

        # Assert not raised as a keyword arg
        _one_arg_with_default(foo=0)

        # Should raise with both a positional arg and a kwarg
        with pytest.raises(MapSDKException):
            _one_arg_with_default(0, kwarg="bar")

    def test_two_args(self):
        # pylint:disable=unused-argument
        @validate_kwargs(positional_only=None)
        def _two_args(foo: int = 1, bar: int = 2, **kwargs):
            pass

        # Assert not raised with no args
        _two_args()

        # Assert not raised as a positional arg
        _two_args(1, 2)

        # Assert not raised as a keyword arg
        _two_args(foo=1, bar=2)

        # Doesn't raise with one positional arg and one keyword arg
        _two_args(1, bar=2)

        # Should raise with both a positional arg and a kwarg
        with pytest.raises(MapSDKException):
            _two_args(1, 2, kwarg=3)

    def test_positional_only_arg(self):
        # pylint:disable=unused-argument
        @validate_kwargs(positional_only=["foo"])
        def _positional_only_arg(foo: int = 1, **kwargs):
            pass

        # Assert not raised with no args
        _positional_only_arg()

        # Assert not raised as a positional arg
        _positional_only_arg(1)

        # Assert raised as a kwarg
        with pytest.raises(MapSDKException):
            _positional_only_arg(foo=1)

        # Should raise with both a positional arg and a kwarg
        with pytest.raises(MapSDKException):
            _positional_only_arg(1, kwarg=3)

    def test_one_arg_on_class_method(self):
        class TestClass:
            # Default params are positional_only=None
            # pylint:disable=unused-argument
            @validate_kwargs()
            def _one_arg(self, foo: int, **kwargs):
                pass

        instance = TestClass()

        # Assert not raised as a positional arg
        instance._one_arg(0)

        # Assert not raised as a keyword arg
        instance._one_arg(foo=0)

        # Should raise with both a positional arg and a kwarg
        with pytest.raises(MapSDKException):
            instance._one_arg(0, kwarg="bar")

    def test_default_none(self):
        class PydanticModel:
            foo: int

        class TestClass:
            # Default params are positional_only=None
            # pylint:disable=unused-argument
            @validate_kwargs()
            def _default_none(
                self, values: Union[PydanticModel, dict, None] = None, **kwargs
            ):
                pass

        instance = TestClass()

        # Assert not raised as a positional arg
        instance._default_none({"foo": 1})

        # Assert not raised as a keyword arg
        instance._default_none(foo=1)

        # Should raise with both a positional arg and a kwarg
        with pytest.raises(MapSDKException):
            instance._default_none({"foo": 1}, foo=1)

        # Should not raise if the positional arg is None
        instance._default_none(None, foo=1)

    def test_add_dataset(self):
        dataset_api = DatasetApiInteractiveMixin()
        dataset_api.transport = MockInteractiveTransport()

        dataset = {"type": "local", "data": "abc"}
        dataset_api.add_dataset(dataset, auto_create_layers=False)
