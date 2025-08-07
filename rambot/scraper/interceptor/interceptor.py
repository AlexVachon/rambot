import os
import time
import json
import tempfile
import subprocess


class Interceptor:

    def __init__(self, scraper):
        self._scraper = scraper
        self._requests_path = os.path.join(tempfile.gettempdir(), f"__{self._scraper.__class__.__name__.lower()}_requests.json")


    def start(self) -> None:
        """
        Start mitmproxy in a separate process with custom env.
        """
        try:
            os.remove(self._requests_path)
        except FileNotFoundError:
            pass

        def run_mitmproxy():

            script_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "mitmproxy_interceptor.py")
            )

            mitmproxy_command = [
                "mitmdump",
                "-s", script_path,
                "--set", f"requests_path={self._requests_path}",
                "--listen-port", self._scraper.proxy_port(),
                "--quiet"
            ]

            env = os.environ.copy()
            env["REQUESTS_PATH"] = self._requests_path

            subprocess.Popen(mitmproxy_command, env=env)
            time.sleep(2)

        run_mitmproxy()


    def get_requests(self) -> list:
        if not os.path.exists(self._requests_path):
            return []

        with open(self._requests_path, "r") as f:
            requests = [json.loads(line) for line in f.readlines()]

        return requests


    def stop(self) -> None:
        """
        Stop mitmproxy
        """
        try:
            os.remove(self._requests_path)
        except FileNotFoundError:
            pass
        subprocess.call(['pkill', 'mitmdump'])