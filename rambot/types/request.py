import re
import json

from typing import Any, Literal, Optional, Dict as TypingDict, Union, List
from urllib.parse import urlparse

ResourceType = Literal[
    "fetch", "document", "stylesheet", "script", 
    "font", "image", "manifest", "media", "other"
]

HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

class DotDict(TypingDict[str, Any]):
    """Base class allowing dot notation access while remaining a native dict."""
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

class Response(DotDict):
    url: str
    status: int
    headers: TypingDict[str, str]
    body: str

    def __init__(self, url: str, status: int, headers: TypingDict[str, str], body: str):
        super().__init__(url=url, status=status, headers=headers, body=body)

    def json(self) -> Optional[Union[TypingDict[str, Any], List[Any]]]:
        try:
            return json.loads(self.body)
        except (json.JSONDecodeError, TypeError):
            return None

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 400

    @property
    def content_type(self) -> str:
        return self.headers.get("Content-Type", "").lower()

class Request(DotDict):
    method: HTTPMethod
    url: str
    headers: TypingDict[str, str]
    body: Any
    response: Response

    def __init__(self, method: HTTPMethod, url: str, headers: TypingDict[str, str], body: str, response: Response):
        super().__init__(method=method, url=url, headers=headers, body=body, response=response)

    @property
    def extension(self) -> str:
        path = urlparse(self.url).path
        match = re.search(r'\.([a-zA-Z0-9]+)$', path)
        return match.group(1).lower() if match else ""

    @property
    def resource_type(self) -> ResourceType:
        """
        Mimics Browser DevTools categorization with strict Literal typing.
        """
        ct = self.response.content_type
        ext = self.extension

        if "json" in ct or "api." in self.url or "/api/" in self.url:
            return "fetch"
        if "html" in ct or ext in ["html", "htm", "php", "asp"]:
            return "document"
        if "css" in ct or ext == "css":
            return "stylesheet"
        if "javascript" in ct or ext in ["js", "mjs"]:
            return "script"
        if "image" in ct or ext in ["webp", "png", "gif", "jpg", "jpeg", "svg", "ico"]:
            return "image"
        if "font" in ct or ext in ["woff", "woff2", "ttf", "otf"]:
            return "font"
        if "manifest" in ct or ext in ["webmanifest", "manifest"]:
            return "manifest"
        if any(t in ct for t in ["video", "audio"]) or ext in ["mp4", "webm", "mp3"]:
            return "media"

        return "other"

    @property
    def is_fetch(self) -> bool: return self.resource_type == "fetch"
    @property
    def is_doc(self) -> bool: return self.resource_type == "document"
    @property
    def is_js(self) -> bool: return self.resource_type == "script"
    @property
    def is_img(self) -> bool: return self.resource_type == "image"

    @property
    def host(self) -> str:
        return urlparse(self.url).netloc
