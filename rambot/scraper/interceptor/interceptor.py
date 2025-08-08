import os
import time
import json
import subprocess
from typing import List

from ...types.interceptor import IInterceptor


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
            "--quiet"
        ]

        env = os.environ.copy()
        env["REQUESTS_PATH"] = self._requests_path

        subprocess.Popen(mitmproxy_command, env=env)
        self.logger.debug(
            "Requests interceptor started ...",
        )
        self._scraper.sleep(time=2)


    def stop(self) -> None:
        try:
            os.remove(self._requests_path)
        except FileNotFoundError:
            pass
        subprocess.call(["pkill", "mitmdump"])
        self.logger.debug(
            "Requests interceptor stopped.",
        )

    
    def get_requests(self) -> List[dict]:
        if not os.path.exists(self._requests_path):
            return []

        with open(self._requests_path, "r") as f:
            return [json.loads(line) for line in f if line.strip()]