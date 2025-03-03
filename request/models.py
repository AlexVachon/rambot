from botasaurus_requests import Response

from typing import TypedDict, Optional, Dict, Any, Union
from typing_extensions import Literal

from bs4 import BeautifulSoup


ALLOWED_METHODS = Literal["GET", "POST"]


class ProxiesOptions(TypedDict, total=False):
    http: str
    https: str


class HeadersOptions(TypedDict, total=False):
    accept: str
    accept_encoding: str
    accept_language: str
    authorization: str
    cache_control: str
    connection: str
    content_length: str
    content_type: str
    cookie: str
    dnt: str
    host: str
    origin: str
    referer: str
    user_agent: str
    x_requested_with: str


def normalize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    return {key.lower(): value for key, value in headers.items()}



class RequestOptions(TypedDict, total=False):
    params: Optional[Dict[str, Any]]
    data: Optional[Union[Dict[str, Any], str, bytes]]
    headers: HeadersOptions
    browser: Optional[Literal["firefox", "chrome"]]
    os: Optional[Literal["windows", "mac", "linux"]]
    user_agent: Optional[str]
    cookies: Optional[Dict[str, str]]
    files: Optional[Dict[str, Any]]
    auth: Optional[Union[tuple, Any]]
    timeout: Optional[Union[int, float]]
    allow_redirects: bool
    proxies: Optional[ProxiesOptions]
    hooks: Optional[Dict[str, Any]]
    stream: Optional[bool]
    verify: Optional[Union[bool, str]]
    cert: Optional[Union[str, tuple]]
    json: Optional[Dict[str, Any]]
    
ResponseContent = Union[Dict[str, Any], BeautifulSoup, str, Response]