from botasaurus_requests import Response
from botasaurus.soupify import soupify, BeautifulSoup

from typing import Union, Dict, Any

from .exceptions import ParsingError

def parse_response(response: Response) -> Union[Dict[str, Any], BeautifulSoup, str, Response]:
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
    