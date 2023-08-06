from functools import wraps


def pass_function_name(func):
    """Pass the decorated function's name as its first argument.
    Useful for logging in XRAY to see which function is being called."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(func.__name__, *args, **kwargs)

    return wrapper
