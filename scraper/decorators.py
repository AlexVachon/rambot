import contextlib
import sys
import os

from functools import wraps
from typing import Callable, List, Type, Optional, Any
from datetime import datetime
import traceback
from pathlib import Path

from .models import ModeResult, ModeStatus

from loguru import logger

@contextlib.contextmanager
def suppress_output():
    with open(os.devnull, 'w') as fnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = fnull, fnull
            yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

def no_print(func):
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
                
                return ModeResult(status=ModeStatus.ERROR, message=error_message)
            
        return wrapper
    return decorator