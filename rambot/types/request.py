import json
from typing import Any, Literal, Optional, Dict as TypingDict, TypeVar, Union, List

HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

class DotDict(TypingDict[str, Any]):
    """Base class allowing dot notation access while remaining a native dict."""
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

class Response(DotDict):
    """A JSON-serializable Response supporting dot notation and autocomplete."""
    url: str
    status: int
    headers: TypingDict[str, str]
    body: str

    def __init__(self, url: str, status: int, headers: TypingDict[str, str], body: str):
        super().__init__(url=url, status=status, headers=headers, body=body)

    def json(self) -> Optional[Union[TypingDict[str, Any], List[Any]]]:
        """Parses and returns the response body as JSON."""
        try:
            return json.loads(self.body)
        except (json.JSONDecodeError, TypeError):
            return None

class Request(DotDict):
    """A JSON-serializable Request supporting dot notation and autocomplete."""
    method: HTTPMethod
    url: str
    headers: TypingDict[str, str]
    body: Any
    response: Response

    def __init__(
        self, 
        method: HTTPMethod, 
        url: str, 
        headers: TypingDict[str, str], 
        body: str, 
        response: Response
    ):
        super().__init__(
            method=method,
            url=url,
            headers=headers,
            body=body,
            response=response
        )
    
    def has_body(self) -> bool:
        """Checks if the request has a non-empty body."""
        return bool(self.body)