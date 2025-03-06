import os
import sys
import contextlib
from functools import wraps

@contextlib.contextmanager
def suppress_output():
    """
    Context manager that temporarily suppresses the standard output (stdout)
    and standard error (stderr) by redirecting them to os.devnull. This can
    be useful when you want to suppress any output (e.g., print statements or errors)
    within a specific block of code.

    Usage:
        with suppress_output():
            # Code inside this block will not produce any output
            # to stdout or stderr.
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
    Decorator that suppresses the standard output (stdout) and standard error (stderr)
    when applied to a function. The decorated function will not produce any output
    when it is called.

    Args:
        func (function): The function to decorate. Its output will be suppressed.

    Returns:
        function: The wrapped function that suppresses its output when called.

    Usage:
        @no_print
        def my_function():
            print("This output will be suppressed.")
            # Output will not be shown in the console.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with suppress_output():
            return func(*args, **kwargs)
    return wrapper
