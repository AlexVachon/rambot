import os
import subprocess

from typing import Optional, Callable
from ...types import IInterceptor, Request, Requests


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
    ) -> Requests:
        requests_to_filter = self._requests()

        if predicate is None:
            return requests_to_filter
        
        filtered = []

        for req in requests_to_filter:
            if predicate(req):
                filtered.append(req)

        return Requests(filtered)