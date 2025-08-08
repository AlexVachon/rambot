class Response:
    def __init__(self, url: str, status_code: int, headers: dict, body: str):
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self._body = body

    @property
    def text(self) -> str:
        return self._body

    def json(self):
        import json
        return json.loads(self._body)
    
    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "status_code": self.status_code,
            "headers": self.headers,
            "body": self._body
        }


class Request:
    def __init__(self, method: str, url: str, headers: dict, body: str, response: Response):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body
        self.response = response

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "response": self.response.to_dict()
        }