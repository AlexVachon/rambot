import os
import json
import subprocess
from typing import List, Optional, Callable, Dict, Any

from ...types import IInterceptor, Request, Response


class Interceptor(IInterceptor):
    def start(self) -> None:
        try:
            os.remove(self._requests_path)
        except FileNotFoundError:
            pass

        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "mitmproxy_interceptor.py")
        )

        mitmproxy_command = [
            "mitmdump",
            "-s", script_path,
            "--set", f"requests_path={self._requests_path}",
            "--listen-port", str(self._scraper.proxy_port()),
            "--ssl-insecure",
            "--quiet"
        ]

        env = os.environ.copy()
        env["REQUESTS_PATH"] = self._requests_path

        subprocess.Popen(mitmproxy_command, env=env)

    def stop(self) -> None:
        try:
            os.remove(self._requests_path)
        except FileNotFoundError:
            pass
        subprocess.call(["pkill", "mitmdump"])

    def requests(self) -> List[Request]:
        if not os.path.exists(self._requests_path):
            return []

        requests_list = []
        with open(self._requests_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)

                    req_data = data["request"]
                    res_data = data["response"]

                    response_obj = Response(
                        url=res_data.get("url", req_data.get("url", "")),
                        status_code=res_data.get("status_code", 0),
                        headers=res_data.get("headers", {}),
                        body=res_data.get("body", "")
                    )

                    request_obj = Request(
                        method=req_data.get("method", ""),
                        url=req_data.get("url", ""),
                        headers=req_data.get("headers", {}),
                        body=req_data.get("body", ""),
                        response=response_obj
                    )

                    requests_list.append(request_obj)
                except json.JSONDecodeError as e:
                    pass

        return requests_list


    def filter_by_url(self, keyword: str, requests: Optional[List[Request]] = None, case_sensitive: bool = False) -> List[Request]:
        requests = requests or self.requests()
        if not case_sensitive:
            keyword = keyword.lower()
            return [r for r in requests if keyword in r.url.lower()]
        else:
            return [r for r in requests if keyword in r.url]


    def filter_by_method(self, method: str, requests: Optional[List[Request]] = None) -> List[Request]:
        method = method.lower()
        requests = requests or self.requests()
        return [r for r in requests if r.method.lower() == method]


    def filter_by_status_code(self, status_codes: List[int], requests: Optional[List[Request]] = None) -> List[Request]:
        """Return requests whose response status code is in the given list."""
        requests = requests or self.requests()
        return [r for r in requests if r.response.status_code in status_codes]


    def filter_by_header(self, header_name: str, header_value: Optional[str] = None, requests: Optional[List[Request]] = None, case_sensitive: bool = False) -> List[Request]:
        requests = requests or self.requests()
        header_name_lower = header_name.lower()
        if header_value is None:
            return [r for r in requests if any(k.lower() == header_name_lower for k in r.headers)]
        else:
            if not case_sensitive:
                header_value = header_value.lower()
                return [
                    r for r in requests
                    if any(k.lower() == header_name_lower and header_value in v.lower() for k, v in r.headers.items())
                ]
            else:
                return [
                    r for r in requests
                    if any(k == header_name and header_value in v for k, v in r.headers.items())
                ]


    def filter_by_response_encoding(self, encoding: str, requests: Optional[List[Request]] = None) -> List[Request]:
        requests = requests or self.requests()
        encoding = encoding.lower()
        return [
            r for r in requests
            if r.response.encoding.lower() == encoding
        ]


    def find_first(self, predicate: Callable[[Request], bool], requests: Optional[List[Request]] = None) -> Optional[Request]:
        requests = requests or self.requests()
        for req in requests:
            if predicate(req):
                return req
        return None


    def map_requests(self, func: Callable[[Request], Any], requests: Optional[List[Request]] = None) -> List[Any]:
        requests = requests or self.requests()
        return [func(r) for r in requests]


    def count_by_method(self, requests: Optional[List[Request]] = None) -> Dict[str, int]:
        requests = requests or self.requests()
        counts = {}
        for r in requests:
            method = r.method.upper()
            counts[method] = counts.get(method, 0) + 1
        return counts


    def count_by_status_code(self, requests: Optional[List[Request]] = None) -> Dict[int, int]:
        requests = requests or self.requests()
        counts = {}
        for r in requests:
            code = r.response.status_code
            counts[code] = counts.get(code, 0) + 1
        return counts