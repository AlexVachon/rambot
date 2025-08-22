import os
import signal
import psutil
import socket
import time
import requests
import subprocess

from abc import ABC, abstractmethod
from typing import List, Generator

from . import cdp, util


class TabBase(ABC):
    driver: "DriverBase"
    target_id: str
    type: str
    title: str
    url: str
    attached: bool = False
    browser_context_id: str
    can_access_opener = None
    _session_id: str | None = None

    def __init__(self, driver: "DriverBase", target_info: dict):
        self.driver = driver
        self.target_id = target_info.get("targetId")
        self.type = target_info.get("type")
        self.title = target_info.get("title")
        self.url = target_info.get("url")
        self.attached = target_info.get("attached", False)
        self.browser_context_id = target_info.get("browserContextId")
        self.can_access_opener = target_info.get("canAccessOpener", None)
        self._session_id = None

    def __repr__(self):
        active_marker = " [CURRENT]" if self.driver.tab is self else ""
        return (
            f"<Tab id={self.target_id} "
            f"type={self.type} title={self.title!r} url={self.url!r}{active_marker}>"
        )

    @abstractmethod
    def activate(self) -> "TabBase":
        pass


class DriverBase(ABC):
    port: int
    chromedriver_path: str
    headless: bool
    session_id: str | None = None
    process: subprocess.Popen[bytes]
    _tabs: List[TabBase]
    _tab: TabBase | None = None

    def __init__(self, chromedriver_path: str = "chromedriver", headless: bool = False, port: int = 9515):
        self.port = port
        self.chromedriver_path = chromedriver_path
        self.headless = headless
        self.session_id = None

        self.process = subprocess.Popen(
            [self.chromedriver_path, f"--port={self.port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        self._wait_for_driver()
        self._start_session()
        self._wait_for_chrome_ready()

        self._run_cdp_command(cdp.network.enable())
        self._run_cdp_command(cdp.target.enable())

    def _run_cdp_command(self, gen: Generator, wait_seconds: int = 1, session_id: str | None = None):
        payload = next(gen)

        cmd = payload["method"]
        params = payload.get("params", {})

        body = {"cmd": cmd, "params": params}
        if session_id:
            body["sessionId"] = session_id

        r = requests.post(
            f"http://localhost:{self.port}/session/{self.session_id}/chromium/send_command_and_get_result",
            json=body
        )
        r.raise_for_status()
        time.sleep(wait_seconds)
        try:
            return gen.send(r.json()["value"])
        except StopIteration as result:
            return result.value

    def _start_session(self):
        chrome_args = [
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-client-side-phishing-detection",
            "--disable-default-apps",
            "--disable-hang-monitor",
            "--disable-popup-blocking",
            "--disable-sync",
            "--disable-translate",
            "--metrics-recording-only",
            "--no-first-run",
            "--remote-debugging-port=9222"
        ]

        if self.headless:
            chrome_args.append("--headless=new")

        payload = {
            "capabilities": {
                "alwaysMatch": {
                    "goog:chromeOptions": {
                        "args": chrome_args
                    }
                }
            }
        }

        response = requests.post(f"http://localhost:{self.port}/session", json=payload)
        response.raise_for_status()
        self.session_id = response.json()["value"]["sessionId"]

    def _wait_for_driver(self, timeout=10):
        start = time.time()
        while True:
            try:
                with socket.create_connection(("localhost", self.port), timeout=1):
                    return
            except (ConnectionRefusedError, OSError):
                if time.time() - start > timeout:
                    raise TimeoutError("ChromeDriver did not start in time")
                time.sleep(0.1)

    def _wait_for_chrome_ready(self, timeout=10):
        return util.execute_with_wait(
            lambda: self._run_cdp_command(cdp.page.enable(), wait_seconds=5),
            timeout=timeout
        )

    def quit(self):
        if self.session_id:
            try:
                requests.delete(f"http://localhost:{self.port}/session/{self.session_id}")
            except Exception:
                pass
            self.session_id = None

        if self.process:
            try:
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.terminate()
                _, alive = psutil.wait_procs(children, timeout=3)
                for p in alive:
                    p.kill()
                parent.terminate()
                parent.wait(3)
            except Exception:
                try:
                    os.kill(self.process.pid, signal.SIGTERM)
                except Exception:
                    pass
            finally:
                self.process = None

    @property
    @abstractmethod
    def tab(self):
        pass

    @tab.setter
    @abstractmethod
    def tab(self, tab: "TabBase"):
        pass

    @property
    @abstractmethod
    def tabs(self):
        pass