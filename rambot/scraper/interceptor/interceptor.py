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

    def requests(
        self,
        predicate: Optional[Callable[[Request], bool]] = None
    ) -> List[Request]:
        requests_to_filter = self._requests()

        if predicate is None:
            return requests_to_filter
        
        filtered = []

        for req in requests_to_filter:
            if predicate(req):
                filtered.append(req)

        return filtered

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