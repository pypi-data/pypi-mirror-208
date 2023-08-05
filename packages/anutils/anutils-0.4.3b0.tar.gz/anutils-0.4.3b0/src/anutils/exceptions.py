import functools
import warnings


def _deprecated(func):
    """Decorator to mark functions as deprecated."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"Function {func.__name__} is deprecated and will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return wrapper