class Response:
    def __init__(self, url: str, status_code: int, headers: dict, body: str):
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self._body = body

    @property
    def text(self) -> str:
        """Returns the response body as text."""
        return self._body

    def json(self):
        """Parses and returns the response body as JSON."""
        import json
        try:
            return json.loads(self._body)
        except Exception:
            return None

    def get_header(self, name: str, default=None):
        """Case-insensitive header lookup."""
        for key, value in self.headers.items():
            if key.lower() == name.lower():
                return value
        return default

    @property
    def ok(self) -> bool:
        """Returns True if the status code is between 200 and 399."""
        return 200 <= self.status_code < 400

    @property
    def is_redirect(self) -> bool:
        """Returns True if status code is a redirect."""
        return self.status_code in {301, 302, 303, 307, 308}

    @property
    def encoding(self) -> str:
        """Return encoding from headers or default to utf-8."""
        content_type = self.get_header('Content-Type', '')
        if 'charset=' in content_type:
            return content_type.split('charset=')[-1]
        return 'utf-8'

    @property
    def content(self) -> bytes:
        """Return the response body as bytes."""
        return self._body.encode(self.encoding)

    def raise_for_status(self):
        """Raises an HTTPError if the status code indicates an error."""
        if not self.ok:
            raise Exception(f"HTTP Error: Status code {self.status_code} for URL {self.url}")

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "status_code": self.status_code,
            "headers": self.headers,
            "body": self._body
        }

    def __repr__(self):
        return f"<Response [{self.status_code}] url=\"{self.url}\">"


class Request:
    def __init__(self, method: str, url: str, headers: dict, body: str, response: Response):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body
        self.response = response

    def get_header(self, name: str, default=None):
        """Case-insensitive header lookup."""
        for key, value in self.headers.items():
            if key.lower() == name.lower():
                return value
        return default

    def has_body(self) -> bool:
        """Return True if the request has a non-empty body."""
        return bool(self.body)

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "response": self.response.to_dict()
        }

    def __repr__(self):
        return f"<Request [{self.method}] url=\"{self.url}\">"