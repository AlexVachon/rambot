import contextlib
import sys
import os

from functools import wraps


@contextlib.contextmanager
def suppress_output():
    """
    Context manager to suppress standard output (stdout) and standard error (stderr).

    This context manager temporarily redirects the `stdout` and `stderr` streams to `os.devnull`,
    effectively silencing any output during the execution of the enclosed block of code.

    Usage:
        with suppress_output():
            # Code inside this block will not print anything to the console.
    """
    with open(os.devnull, 'w') as fnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = fnull, fnull
            yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr


def no_print(func):
    """
    Decorator that suppresses output (stdout and stderr) for the decorated function.

    This decorator wraps the decorated function and suppresses any printed output or errors
    when the function is called.

    Args:
        func (Callable): The function to decorate.

    Returns:
        Callable: The wrapped function that suppresses output when called.

    Usage:
        @no_print
        def my_function():
            print("This will not be printed.")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with suppress_output():
            return func(*args, **kwargs)
    return wrapper