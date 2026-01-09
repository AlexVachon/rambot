import typing

from typing_extensions import Literal


class ProxiesOptions(typing.TypedDict, total=False):
    """
    A dictionary representing the proxy settings for HTTP and HTTPS connections.

    This class is used to specify the proxies for both HTTP and HTTPS protocols.

    Attributes:
        http (str): The proxy URL for HTTP requests.
        https (str): The proxy URL for HTTPS requests.
    """
    http: str
    https: str


class HeadersOptions(typing.TypedDict, total=False):
    """
    A dictionary representing various HTTP headers for a request.

    This class defines the most common HTTP headers that can be sent along with a request.

    Attributes:
        accept (str): The `Accept` header for specifying acceptable response content types.
        accept_encoding (str): The `Accept-Encoding` header for specifying acceptable encoding formats.
        accept_language (str): The `Accept-Language` header for specifying the acceptable languages.
        authorization (str): The `Authorization` header for providing credentials.
        cache_control (str): The `Cache-Control` header for controlling caching behavior.
        connection (str): The `Connection` header for specifying the connection type.
        content_length (str): The `Content-Length` header specifying the length of the request body.
        content_type (str): The `Content-Type` header specifying the media type of the resource.
        cookie (str): The `Cookie` header for sending cookies to the server.
        dnt (str): The `DNT` (Do Not Track) header for privacy preferences.
        host (str): The `Host` header for specifying the domain name of the server.
        origin (str): The `Origin` header for identifying the origin of the request.
        referer (str): The `Referer` header for specifying the URL from which the request is made.
        user_agent (str): The `User-Agent` header specifying the client's software.
        x_requested_with (str): The `X-Requested-With` header commonly used for Ajax requests.
    """
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


def normalize_headers(headers: typing.Dict[str, str]) -> typing.Dict[str, str]:
    """
    Normalizes the headers by converting all header keys to lowercase.

    This function takes a dictionary of HTTP headers and returns a new dictionary
    where all header keys are converted to lowercase. This ensures consistency and
    avoids issues with case-sensitive header names.

    Args:
        headers (dict): A dictionary containing HTTP headers.

    Returns:
        dict: A new dictionary with all header keys in lowercase.
    """
    return {key.lower(): value for key, value in headers.items()}



class RequestOptions(typing.TypedDict, total=False):
    """
    A dictionary representing various options for configuring an HTTP request.

    This class is used to specify all the parameters that can be customized when
    making an HTTP request, such as headers, authentication, timeout, proxies, etc.

    Attributes:
        params (dict, optional): Query parameters to be included in the request URL.
        data (dict or str or bytes, optional): Data to be sent with the request body.
        headers (HeadersOptions): Custom headers to send along with the request.
        browser (str, optional): Browser type for simulating specific user agents.
        os (str, optional): Operating system type for simulating specific environments.
        user_agent (str, optional): Custom User-Agent string.
        cookies (dict, optional): Cookies to be sent with the request.
        files (dict, optional): Files to be uploaded with the request.
        auth (tuple or any, optional): Authentication credentials for the request.
        timeout (int or float, optional): Timeout for the request, in seconds.
        allow_redirects (bool): Whether to allow automatic redirects (default is True).
        proxies (ProxiesOptions, optional): Proxy settings for the request.
        hooks (dict, optional): Event hooks for specific request events.
        stream (bool, optional): Whether to stream the response content.
        verify (bool or str, optional): Whether to verify SSL certificates (True or path to cert).
        cert (str or tuple, optional): Client certificate for SSL authentication.
        json (dict, optional): JSON data to be sent with the request.
    """
    params: typing.Optional[typing.Dict[str, typing.Any]]
    data: typing.Optional[typing.Union[typing.Dict[str, typing.Any], str, bytes]]
    headers: HeadersOptions
    browser: typing.Optional[Literal["firefox", "chrome"]]
    os: typing.Optional[Literal["windows", "mac", "linux"]]
    user_agent: typing.Optional[str]
    cookies: typing.Optional[typing.Dict[str, str]]
    files: typing.Optional[typing.Dict[str, typing.Any]]
    auth: typing.Optional[typing.Union[tuple, typing.Any]]
    timeout: typing.Optional[typing.Union[int, float]]
    allow_redirects: bool
    proxies: typing.Optional[ProxiesOptions]
    hooks: typing.Optional[typing.Dict[str, typing.Any]]
    stream: typing.Optional[bool]
    verify: typing.Optional[typing.Union[bool, str]]
    cert: typing.Optional[typing.Union[str, tuple]]
    json: typing.Optional[typing.Dict[str, typing.Any]]

