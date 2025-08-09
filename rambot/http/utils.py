from botasaurus_requests import Response
from botasaurus.soupify import soupify, BeautifulSoup
from typing import Union, Dict, Any

from .exceptions import ParsingError


def parse_response(response: Response) -> Union[Dict[str, Any], BeautifulSoup, str, Response]:
    """
    Parses the HTTP response content based on its content type.

    This function examines the `Content-Type` header of the response and parses
    the body accordingly. It supports parsing JSON, HTML, and plain text responses.
    If the response contains an unsupported content type, the raw response text is returned.

    Args:
        response (Response): The HTTP response object to be parsed.

    Returns:
        Union[Dict[str, Any], BeautifulSoup, str, Response]:
            - If the content is JSON, returns a dictionary parsed from the JSON response.
            - If the content is HTML, returns a `BeautifulSoup` object for parsing and navigating the HTML.
            - If the content is plain text, returns the raw text.
            - In case of unsupported content type, returns the raw text of the response.

    Raises:
        ParsingError: If there is an error parsing the response content, such as invalid JSON or HTML.
    """
    content_type = response.headers.get("Content-Type", "").lower()

    if "application/json" in content_type:
        try:
            return response.json()
        except ValueError as e:
            raise ParsingError(f"Error parsing JSON: {e}") from e
    elif "text/html" in content_type:
        try:
            return soupify(response)
        except Exception as e:
            raise ParsingError(f"Error parsing HTML: {e}") from e
    else:
        return response.text
