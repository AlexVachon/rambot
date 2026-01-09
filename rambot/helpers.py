# helpers.py
import os
import sys
import hashlib
import random
import contextlib

from functools import wraps
from datetime import date, datetime, timezone
from typing import Dict, Optional
from enum import Enum


class By(Enum):
    XPATH = "xpath"
    SELECTOR = "selector"


USER_AGENTS = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",

    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/117.0.0.0",
    
    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Safari/537.36",
    
    # Mobile
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]



def get_proxies(
    host: str, 
    port:str, 
    username: Optional[str] = None, 
    password: Optional[str] = None, 
    include_scheme: bool = False, 
    use_https_scheme: bool = False
) -> Dict[str, str]:
    """Generate a proper proxy information dictionary, including credentials if schemes if required.

    Args:
        host (str): Proxy host.
        port (str): Proxy port.
        username (str, optional): Proxy username if required. Defaults to None.
        password (str, optional): Proxy password if required. Defaults to None.
        include_scheme (bool, optional): Include the http/https scheme if required. Defaults to False.
        use_https_scheme (bool, optional): Force usage of the "https" scheme for the HTTPS proxy. Defaults to False.

    Returns:
        Dict: A dictionary with http and https proxy URLs.
    """
    
    proxy = dict()
    
    http_scheme: str = ""
    https_scheme: str = ""
    
    if include_scheme:
        http_scheme = "http://"
        https_scheme = "https://" if use_https_scheme else https_scheme
    
    if username and username.strip():
        proxy['http'] = f'{http_scheme}{username}:{password}@{host}:{port}'
        proxy['https'] = f'{https_scheme}{username}:{password}@{host}:{port}'
    else:
        proxy['http'] = f'{http_scheme}{host}:{port}'
        proxy['https'] = f'{https_scheme}{host}:{port}'
    
    return proxy


def compute_id(url: str) -> str:
    """Compute a unique identifier for a given URL using the MD5 hash function.

    Args:
        url (str): The input URL to hash.

    Returns:
        str: A hexadecimal string representing the MD5 hash of the URL.
    """
    return hashlib.md5(url.encode()).hexdigest()


def get_current_date_str() -> str:
    """Get the current date as a string formatted as YYYY-MM-DD.

    Returns:
        str: The current date in the format "YYYY-MM-DD".
    """
    return date.today().strftime("%Y-%m-%d")


def get_current_datetime_str() -> str:
    """Get the current UTC date and time as a string.

    Returns:
        str: The current UTC timestamp in ISO 8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)


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
