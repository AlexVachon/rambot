#botminator/scraper.py
from botasaurus.browser import Driver
from botasaurus_driver.core.config import Config

from botasaurus_driver.driver import Element

from .config import ScraperConfig
from .exceptions import DriverError

from .decorators import no_print, errors

from typing import Optional, List, Type

from loguru import logger as default_logger

logger = default_logger

class Scraper:
    def __init__(self, config: Config = None, create_error_logs: bool = False, must_raise: List[Type[Exception]] = None):
        if must_raise is None:
            must_raise = [Exception]
        
        self.create_error_logs = create_error_logs
        self.config = ScraperConfig(**(config or {}))

        self._driver: Optional[Driver] = None

        self.logger = logger

    @property
    def driver(self) -> Optional[Driver]:
        if not hasattr(self, '_driver') or not self._driver:
            self.open()
        return self._driver

    def error_decorator(self):
        return errors(
            must_raise=self.must_raise,
            create_logs=self.create_error_logs
        )

    @no_print
    @error_decorator
    def open(self, wait: bool = True) -> None:
        raise DriverError("Oops! something wrong happened ...")
        driver_config = {
            "headless": False,
            # "proxy": "",
            # "profile": None,
            # "tiny_profile": False,
            # "block_images": False,
            # "block_images_and_css": False,
            "wait_for_complete_page_load": wait,
            # "extensions": [],
            "arguments": [
                "--ignore-certificate-errors",
                "--ignore-ssl-errors=yes"
            ],
            # "user_agent": None,
            # "lang": "en",
            # "beep": False
        }
        self._driver = Driver(**driver_config)
        
        if not self._driver._tab:
            raise DriverError("Impossible d'initialiser le driver")
                
    @no_print
    @error_decorator
    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    @no_print
    @error_decorator
    def get(self, url: str, bypass_cloudflare: bool = False,
                 accept_cookies: bool = False, wait: Optional[int] = None) -> None:
        if self.driver.config.is_new:
            self.driver.google_get(
                link=url,
                bypass_cloudflare=bypass_cloudflare,
                accept_google_cookies=accept_cookies,
                wait=wait or self.config.min_delay
            )
        else:
            response = self.driver.requests.get(url=url)
            response.raise_for_status()
            return response

    @no_print
    @error_decorator
    def find(self, selector: str, timeout: int = 10) -> Optional[Element]:
        return self.driver.select(
            selector=selector,
            wait=min(timeout, self.config.max_delay)
        )