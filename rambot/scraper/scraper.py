import json
import time
import random
import argparse

from botasaurus_driver.driver import Wait
from ..browser.driver import Driver
from .html import HTML

from .. import helpers
from ..logging_config import update_logger_config, get_logger
from ..types import IScraper

from .utils import scrape
from .interceptor import Interceptor
from .models import mode_manager as mode_manager_instance, Mode, ScrapedDocument
from .exception_handler import ExceptionHandler
from .config import ScraperConfig
from .exceptions import DriverError


class Scraper(IScraper):

    mode_manager = mode_manager_instance

    def __init__(self):
        self.logger = get_logger(__name__)
        self._interceptor = Interceptor(scraper=self)
        
        self.setup_driver_config()
        self.setup_exception_handler()
        self.setup()


    # ---- Proxy ----
    def proxy_port(self): return "8080"

    def proxy_host(self): return "localhost"

    def proxy(self, username=None, password=None, include_scheme=False, use_https_scheme=False):
        return helpers.get_proxies(
            host=self.proxy_host(),
            port=self.proxy_port(),
            username=username,
            password=password,
            include_scheme=include_scheme,
            use_https_scheme=use_https_scheme
        )
    

    # ---- Setup ----
    def setup(self):
        parser = argparse.ArgumentParser(description="Launch script with a specific mode")
        parser.add_argument("--mode", type=str, required=True)
        parser.add_argument("--url", type=str, required=False)
        self.args = parser.parse_args()
        
        self.mode_manager.validate(self.args.mode)
        self.mode = self.args.mode
        
        self._target_url = self.args.url
        self.setup_logging(mode=self.mode_manager.get_mode(self.mode))

    def setup_exception_handler(self, must_raise_exceptions=[Exception]):
        self.exception_handler = ExceptionHandler(must_raise_exceptions=must_raise_exceptions)

    def setup_driver_config(self, **kwargs):
        self.config = ScraperConfig(
            headless=kwargs.get("headless", False),
            proxy=kwargs.get("proxy", f"http://{self.proxy_host()}:{self.proxy_port()}"),
            profile=kwargs.get("profile"),
            tiny_profile=kwargs.get("tiny_profile", False),
            block_images=kwargs.get("block_images", False),
            block_images_and_css=kwargs.get("block_images_and_css", False),
            wait_for_complete_page_load=kwargs.get("wait_for_complete_page_load", False),
            extensions=kwargs.get("extensions", []),
            arguments=kwargs.get("arguments", [
                "--ignore-certificate-errors",
                "--ignore-ssl-errors=yes",
                "--disable-blink-features=AutomationControlled"
            ]),
            user_agent=kwargs.get("user_agent"),
            lang=kwargs.get("lang"),
            beep=kwargs.get("beep", False)
        )

    def update_driver_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                self.logger.warning(f"Unknown configuration key: {key}")

    def setup_logging(self, mode: Mode):
        update_logger_config(class_name=self.__class__.__name__, log_to_file=mode.enable_file_logging, file_path=mode.log_file_name if mode.enable_file_logging else None)


    # ---- Run ----
    def run(self):
        try:
            if not hasattr(self, "args") or not hasattr(self.args, "mode"):
                raise RuntimeError("Calling .run() without calling .setup() first")
            
            self._interceptor.start()

            method = self.mode_manager.get_func(self.mode)
            decorated_method = scrape(method)
            result = decorated_method(self)

            self._interceptor.stop()
            
            return result
        except Exception as e:
            self.exception_handler.handle(e)


    # ---- Interceptor ----
    @property
    def interceptor(self) -> Interceptor:
        """
        Get the request interceptor instance.

        Lazily initializes an Interceptor associated with this scraper if one 
        does not already exist.

        Returns:
            Interceptor: The instance managing network interception for this scraper.
        """
        if not hasattr(self, "_interceptor"):
            self._interceptor = Interceptor(scraper=self)
        return self._interceptor


    # ---- Browser ----
    @property
    def driver(self):
        if not self._driver:
            self.open_browser()
        return self._driver

    @helpers.no_print
    def open_browser(self, wait=True):
        try:
            self.logger.debug(f"Opening browser (Headless: {self.config.headless}) ...")

            is_headless = bool(self.config.headless)
            
            self._driver = Driver(
                headless=is_headless,
                proxy=self.config.proxy,
                profile=self.config.profile,
                tiny_profile=self.config.tiny_profile,
                block_images=self.config.block_images,
                block_images_and_css=self.config.block_images_and_css,
                wait_for_complete_page_load=wait,
                extensions=self.config.extensions,
                arguments=self.config.arguments or [],
                user_agent=self.config.user_agent,
                lang=self.config.lang,
                beep=self.config.beep,
            )

            if not self._driver._tab:
                raise DriverError("Can't initialize driver tab")
                
        except Exception as e:
            self.exception_handler.handle(e)

    @helpers.no_print
    def close_browser(self):
        try:
            self.logger.debug("Closing browser...")
            if self._driver:
                self._driver.close()
                self._driver = None
        except Exception as e:
            self.exception_handler.handle(e)


    # ---- Navigation ----
    @helpers.no_print
    def load_page(self, url, bypass_cloudflare=False, accept_cookies=False, wait=5, timeout=30):
        try:
            if self.driver.config.is_new:
                self.driver.google_get(
                    link=url,
                    bypass_cloudflare=bypass_cloudflare,
                    accept_google_cookies=accept_cookies,
                    wait=wait,
                    timeout=timeout
                )
                self.logger.debug("Page is loaded")
            else:
                response = self.driver.requests.get(url=url)
                response.raise_for_status()

                self.logger.debug("Page is loaded")

                return response
        except Exception as e:
            self.exception_handler.handle(e)

    def get_current_url(self):
        try: return self.driver.current_url
        except Exception as e: self.exception_handler.handle(e)

    def refresh_page(self):
        try: self.driver.reload()
        except Exception as e: self.exception_handler.handle(e)

    def execute_script(self, script):
        try: return self.driver.run_js(script)
        except Exception as e: self.exception_handler.handle(e)

    def navigate_back(self): self.execute_script("window.history.back()")

    def navigation_forward(self): self.execute_script("window.history.forward()")


    # ---- Elements ----
    @property
    def html(self):
        if not self._html:
            self._html = HTML(driver=self.driver)
        return self._html

    
    # ---- Storage ----
    def get_cookies(self): return self.driver.get_cookies()

    def add_cookies(self, cookies): self.driver.add_cookies(cookies)

    def delete_cookies(self): self.driver.delete_cookies()

    def get_local_storage(self): return self.driver.get_local_storage()

    def add_local_storage(self, local_storage): self.driver.add_local_storage(local_storage)

    def delete_local_storage(self): self.driver.delete_local_storage()


    # ---- Scroll ----
    def scroll(self, selector=None, by=1000, smooth_scroll=True, wait=Wait.SHORT): self.driver.scroll(selector, by, smooth_scroll, wait)

    def scroll_to_bottom(self, selector=None, smooth_scrolling=True, wait=Wait.SHORT): self.driver.scroll_to_bottom(selector, smooth_scrolling, wait)

    def scroll_to_element(self, selector, wait=Wait.SHORT): self.driver.scroll_into_view(selector, wait)


    # ---- Utils ----
    def sleep(self, t = None):
        if t is None:
            return
        self.logger.debug(f"Waiting {t}s ...")
        time.sleep(t)

    def wait(self, min=0.1, max=1):
        delay = random.uniform(min, max)
        self.logger.debug(f"Waiting {delay}s ...")

        time.sleep(delay)

    def save(self, data: list[ScrapedDocument]):
        try:
            self.write(data=data)
            self.logger.debug(f"Saved {len(data)} document(s)")
        except Exception as e:
            self.exception_handler.handle(e)

    def write(self, data):
        try:
            with open(f"{self.mode}.json", 'w') as file:
                json.dump([d.to_dict() for d in data], file, indent=4)
        except Exception as e:
            self.exception_handler.handle(e)

    def read(self, filename):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except Exception as e:
            self.exception_handler.handle(e)

    def create_document(self, obj, document):
        try:
            return document(**obj.get("document", {}))
        except Exception as e:
            self.exception_handler.handle(e)