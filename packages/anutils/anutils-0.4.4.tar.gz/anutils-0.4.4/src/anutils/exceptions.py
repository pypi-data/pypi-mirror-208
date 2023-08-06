import functools
import warnings


def _deprecated(message=None):
    """Decorator to mark functions as deprecated."""

    msg = message

    def decorator(func):

        message = f"Function {func.__name__} is deprecated and will be removed in a future version."
        if message is not None:
            message += f" {msg}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator