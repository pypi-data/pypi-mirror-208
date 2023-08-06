from functools import wraps
from inspect import Parameter, signature
from typing import Any, Callable, Optional, Sequence, TypeVar

from unfolded.map_sdk.errors import MapSDKException

__all__ = ("validate_kwargs", "assert_not_rendered")

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def validate_kwargs(*, positional_only: Optional[Sequence[str]] = None):
    """Checks to make sure both positional args and kwargs are not used"""

    def decorator(func: FuncT) -> FuncT:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Inspect the signature of the function
            sig = signature(func)

            # Record the names of explicit keyword parameters that should not be considered to go
            # into the **kwargs catch-all
            explicit_named_parameters = {
                param_name
                for param_name, param in sig.parameters.items()
                if param.kind == Parameter.KEYWORD_ONLY
            }

            # None can be passed in explicitly to positional args
            # Needed for to subclasses to be able to call super().{method}
            n_args_used = len([arg for arg in args if arg is not None])

            # Number of positional arguments
            # If this decorator is used, it's assumed that at least one of these is not intended to
            # be used at the same time as the `kwargs` catch-all.
            n_args = len(
                [
                    param
                    for param in sig.parameters.values()
                    if param.kind
                    in [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
                ]
            )

            extra_kwargs = set(kwargs.keys()).difference(explicit_named_parameters)

            if n_args_used >= n_args and len(extra_kwargs) > 0:
                kwarg_list = ", ".join(f"'{kwarg}'" for kwarg in extra_kwargs)
                raise MapSDKException(
                    f"{kwarg_list} cannot be passed in with both positional arguments and kwargs, use one or the other."
                )

            # Language support for declaring positional-only arguments with / began in 3.8, and we
            # support 3.7
            # https://peps.python.org/pep-0570/
            if positional_only:
                positional_only_used = set(kwargs.keys()).intersection(positional_only)
                if len(positional_only_used) == 1:
                    raise MapSDKException(
                        f"'{list(positional_only_used)[0]}' is a positional-only argument."
                    )
                elif len(positional_only_used) > 1:
                    arg_list = ", ".join(f"'{arg}'" for arg in positional_only_used)
                    raise MapSDKException(f"{arg_list} are positional-only arguments.")

            return func(*args, **kwargs)

        # Incompatible return value type (got "Callable[[VarArg(Any), KwArg(Any)], Any]", expected "FuncT")
        return wrapper  # type:ignore[return-value]

    return decorator


def assert_not_rendered(func):
    """Assert that the class has not yet been rendered before calling this function"""

    @wraps(func)
    def wrap(self, *args, **kwargs):
        if self.rendered:
            raise MapSDKException(
                f"Cannot call {func.__name__} on already-rendered map"
            )

        return func(self, *args, **kwargs)

    return wrap
