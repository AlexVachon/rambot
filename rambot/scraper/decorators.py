import contextlib
import sys
import os

from functools import wraps
from typing import Callable, List, Type, Optional, Any
from datetime import datetime
import traceback
from pathlib import Path

from loguru import logger


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


def errors(
    must_raise: List[Type[Exception]] = [Exception],
    create_logs: bool = False,
    log_level: str = "WARNING",
    log_format: Optional[str] = None
) -> Callable:
    """
    Decorator for handling errors and logging them.

    This decorator allows you to specify which exceptions should be raised, whether error logs
    should be created, and the logging level and format. If an exception occurs, it will log the error
    to a file and optionally raise it based on the configuration.

    Args:
        must_raise (List[Type[Exception]], optional): List of exception types that should be raised.
            Defaults to raising any exception.
        create_logs (bool, optional): Whether to create error logs when an exception occurs. Defaults to False.
        log_level (str, optional): The level at which the error should be logged. Defaults to "WARNING".
        log_format (str, optional): The format string for log messages. Defaults to a predefined format.

    Returns:
        Callable: The decorated function with error handling and logging.

    Usage:
        @errors(must_raise=[ValueError], create_logs=True)
        def my_function():
            # This function will log errors and raise a ValueError if it occurs.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            try:
                effective_must_raise = must_raise(self) if callable(must_raise) else must_raise
                effective_create_logs = create_logs(self) if callable(create_logs) else create_logs

                return func(self, *args, **kwargs)
            except Exception as e:
                if effective_create_logs:
                    log_dir = Path("errors")
                    log_dir.mkdir(exist_ok=True)

                    format_str = log_format or "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

                    handlers = [getattr(h, "baseFilename", None) for h in logger._core.handlers.values()]
                    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

                    if str(log_file) not in handlers:
                        logger.add(
                            log_file,
                            level=log_level,
                            format=format_str
                        )

                error_message = f"Error in {func.__name__}: {str(e)}"
                traceback_details = traceback.format_exc()

                getattr(logger, log_level.lower())(
                    f"{error_message}\n{traceback_details}"
                )

                if any(isinstance(e, exc_type) for exc_type in effective_must_raise):
                    raise e

        return wrapper

    return decorator
