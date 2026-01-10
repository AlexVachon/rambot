from .utils import parse_response

from ..logging_config import get_logger

from botasaurus.request import request as request_decorator, Request
from requests.exceptions import RequestException

from .exceptions import MethodError, RequestFailure, OptionsError
from .models import RequestOptions, normalize_headers
from ..helpers import no_print

from pydantic import HttpUrl

from typing import Optional, Literal, Union, Dict, Any
from bs4 import BeautifulSoup
from botasaurus_requests import Response

import json

logger = get_logger(__name__)


@no_print
def request(
    method: Literal["GET", "POST"],
    url: HttpUrl,
    options: RequestOptions = {}, 
    max_retry: Optional[int] = 5, 
    retry_wait: Optional[int] = 5, 
    parsed: bool = False
) -> Union[Dict[str, Any], BeautifulSoup, str, Response]:
    """
    Sends an HTTP request using the specified method and options.

    This function supports automatic retries and optional response parsing. 
    It wraps the request execution with error handling and logging.

    Args:
        method (Literal["GET", "POST"]): The HTTP method to use (e.g., "GET", "POST").
        url (HttpUrl): The target URL for the HTTP request.
        options (RequestOptions, optional): The request options, such as headers, params, data, etc.
            Defaults to an empty dictionary.
        max_retry (Optional[int], optional): Maximum number of retry attempts in case of failure.
            Defaults to 5.
        retry_wait (Optional[int], optional): Delay (in seconds) between retry attempts. Defaults to 5.
        raw (bool, optional): If `True`, returns the raw HTTP response instead of parsing it.
            Defaults to `False`.

    Returns:
        Union[Dict[str, Any], BeautifulSoup, str, Response]: The parsed response if `raw` is `False`, otherwise the raw HTTP response.

    Raises:
        MethodError: If an unsupported HTTP method is used.
        RequestFailure: If the request fails due to an unknown error or a request exception.
        OptionsError: If there is an issue with the provided options.
    
    Example:
        ```python
        content = requests(
            method="GET",
            url="http://example.com",
            options={
                "proxies": {
                    "http": "http://my-proxy.com:{port}",
                    "https": "http://my-proxy.com:{port}"
                },
                "timeout": 10,
                "verify": False,
                "os": "windows",
                "browser": "chrome"
            },
            max_retry=10,
            retry_wait=2.5
        )
        ```
    """
    
    logger.debug(f"Trying to load \"{url}\" ...")
    
    @request_decorator(
        max_retry=max_retry,
        retry_wait=retry_wait,
        output=None,
        create_error_logs=False,
        output_formats=[Union[Dict[str, Any], BeautifulSoup, str, Response]],
        raise_exception=True,
        close_on_crash=True,
        must_raise_exceptions=[MethodError, OptionsError]
    )
    def send_request(request: Request, data: RequestOptions):
        """
        Sends the actual HTTP request using the specified method and options.

        This inner function is responsible for making the request using the method (GET or POST),
        handling errors, and parsing the response.

        Args:
            request (Request): The decorated request object to send the HTTP request.
            data (RequestOptions): The options dictionary containing request parameters, headers, etc.

        Returns:
            Union[Dict[str, Any], BeautifulSoup, str, Response]: The response from the server, either parsed or raw based on the `raw` flag.

        Raises:
            MethodError: If an unsupported HTTP method is used.
            RequestFailure: If the request fails due to an error or exception.
            OptionsError: If there are issues with the provided options.
        """
        try:
            if "headers" not in options or options["headers"] is None:
                data["headers"] = {}
            
            if "json" in data:
                data["json"] = json.dumps(data["json"], ensure_ascii=False)
            
            data["headers"] = normalize_headers(data.get("headers", {}))
            
            if method == "GET":
                response = request.get(url, **data)
            elif method == "POST":
                response = request.post(url, **data)
            else:
                raise MethodError(method=method)

            response.raise_for_status()

            return parse_response(response=response) if parsed else response

        except MethodError as e:
            raise e
        except RequestException as e:
            logger.warning(e)
            raise RequestFailure(f"Something went wrong in request: {e}")
        except TypeError as e:
            raise OptionsError(f"Options got unexpected values: {e}")
        except Exception as e:
            raise RequestFailure(f"The request has failed for unknown reason: {e}")

    return send_request(data=options)
