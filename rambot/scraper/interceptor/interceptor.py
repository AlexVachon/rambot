import os
import json
import subprocess
from typing import List

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
            "--quiet"
        ]

        env = os.environ.copy()
        env["REQUESTS_PATH"] = self._requests_path

        subprocess.Popen(mitmproxy_command, env=env)
        self.logger.debug("Requests interceptor started ...")
        self._scraper.sleep(t=2)

    def stop(self) -> None:
        try:
            os.remove(self._requests_path)
        except FileNotFoundError:
            pass
        subprocess.call(["pkill", "mitmdump"])
        self.logger.debug("Requests interceptor stopped.")


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
                        url=res_data["url"],
                        status_code=res_data["status_code"],
                        headers=res_data["headers"],
                        body=res_data["body"]
                    )

                    request_obj = Request(
                        method=req_data["method"],
                        url=req_data["url"],
                        headers=req_data["headers"],
                        body=req_data["body"],
                        response=response_obj
                    )

                    requests_list.append(request_obj)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse request log line: {e}")

        return requests_list