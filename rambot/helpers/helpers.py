# helpers/helpers.py
import typing

import hashlib

from datetime import date, datetime, timezone


def get_proxies(
    host: str, 
    port:str, 
    username: typing.Optional[str] = None, 
    password: typing.Optional[str] = None, 
    include_scheme: bool = False, 
    use_https_scheme: bool = False
) -> typing.Dict[str, str]:
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
