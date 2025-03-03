import os
import json
import time 
import random
import argparse

from functools import wraps

from botasaurus.browser import Driver
from botasaurus_driver.driver import Element

from .models import Listing, Document, ScraperModeManager, ModeResult, ModeStatus
from .config import ScraperConfig, ErrorConfig
from .exceptions import DriverError
from .decorators import no_print, errors

from typing import Optional, List, Dict, Any, Callable, Type

from loguru import logger as default_logger

logger = default_logger


class Scraper:
    mode_manager = ScraperModeManager()
    
    ERRORS_CONFIG: ErrorConfig = {
        "must_raise": lambda self: self.config.must_raise,
        "create_logs": lambda self: self.config.create_error_logs
    }
    
    def __init__(
        self, 
        config: ScraperConfig = None
    ):
        self.config = config or ScraperConfig()
        self._driver: Optional[Driver] = None
        self.logger = logger
        
        self.setup()


    def setup(self) -> None:
        parser = argparse.ArgumentParser(description="Launch script with a specific mode")
        parser.add_argument("--mode", type=str, required=True, help="Scraper's mode to start")
        
        self.args = parser.parse_args()
        
        self.mode_manager.validate(self.args.mode)
    
    
    @errors(**ERRORS_CONFIG)
    def run(self) -> None:
        if not hasattr(self, "args") or not hasattr(self.args, "mode"):
            raise RuntimeError("Calling .run() without calling .setup() first")

        self.mode = self.args.mode
        method = self.mode_manager.get_func(self.mode)

        decorated_method = scrape(method)

        decorated_method(self)

        self.logger.debug("Done!")


    @property
    def driver(self) -> Optional[Driver]:
        if not hasattr(self, '_driver') or not self._driver:
            self.open()
        return self._driver


    @no_print
    @errors(**ERRORS_CONFIG)
    def open(
        self, 
        wait: bool = True
    ) -> None:
        self.logger.debug("Opening browser ...")
        
        driver_config = {
            "headless": self.config.headless if self.config.headless is not None else False,
            "proxy": self.config.proxy if self.config.proxy is not None else "",
            "profile": self.config.profile if self.config.profile is not None else None,
            "tiny_profile": self.config.tiny_profile if self.config.tiny_profile is not None else False,
            "block_images": self.config.block_images if self.config.block_images is not None else False,
            "block_images_and_css": self.config.block_images_and_css if self.config.block_images_and_css is not None else False,
            "wait_for_complete_page_load": wait,
            "extensions": self.config.extensions if self.config.extensions else [],
            "arguments": self.config.arguments if self.config.arguments else [
                "--ignore-certificate-errors",
                "--ignore-ssl-errors=yes"
            ],
            "user_agent": self.config.user_agent if self.config.user_agent else None,
            "lang": self.config.lang if self.config.lang else "en",
            "beep": self.config.beep if self.config.beep is not None else False,
        }
        self._driver = Driver(**driver_config)
        
        if not self._driver._tab:
            raise DriverError("Can't initialize driver")
    
    
    @no_print
    @errors(**ERRORS_CONFIG)
    def close(self) -> None:
        self.logger.debug("Closing browser...")
        if self._driver is not None:
            self._driver.close()
            self._driver = None


    @errors(**ERRORS_CONFIG)
    def save(
        self,
        links: List[str],
        document_output: Type[Document]
    ) -> None:
        try:
            formatted_data = [document_output(link=link).output() for link in links]
            
            self.write(data=formatted_data)
            self.logger.debug(f"Saved {len(formatted_data)} links")
        except Exception as e:
            self.logger.error(f"Failed to save links: {e}")
            raise


    @errors(**ERRORS_CONFIG)
    def write(
        self,
        data: List[Type[Document]]
    ) -> None:
        try:
            filename = f"{self.mode}.json"
            
            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
        
        except Exception as e:
            self.logger.warning(f"Failed to write data to {filename}: {e}")
            raise


    @errors(**ERRORS_CONFIG)
    def read(
        self, 
        filename: str
    ) -> Dict[str, List[Listing]]:
        with open(filename, 'r') as file:
            return json.load(file)


    @errors(**ERRORS_CONFIG)
    def create_document(
        self, 
        obj: Dict[str, Any], 
        document: Type[Document]
    ) -> Document:
        return document(**obj)

    
    @no_print
    @errors(**ERRORS_CONFIG)
    def get(
        self, 
        url: str, 
        bypass_cloudflare: bool = False,
        accept_cookies: bool = False, 
        wait: Optional[int] = None
    ) -> None:
        if self.driver.config.is_new:
            self.driver.google_get(
                link=url,
                bypass_cloudflare=bypass_cloudflare,
                accept_google_cookies=accept_cookies,
                wait=wait
            )
            self.logger.debug("Page is loaded")
        else:
            response = self.driver.requests.get(url=url)
            response.raise_for_status()
            
            self.logger.debug("Page is loaded")
            
            return response 
        
        
    @no_print
    @errors(**ERRORS_CONFIG)
    def find_all(
        self, 
        selector: str, 
        timeout: int = 10
    ) -> List[Element]:
        return self.driver.select_all(
            selector=selector,
            wait=timeout
        )
    
    
    @no_print
    @errors(**ERRORS_CONFIG)
    def find(
        self, 
        selector: str, 
        timeout: int = 10
    ) -> Element:
        return self.driver.select(
            selector=selector,
            wait=timeout
        )
    
    
    @errors(**ERRORS_CONFIG)
    def wait(
        self, 
        min: float = 0.1, 
        max: float = 1
    ) -> None:
        delay = random.uniform(min, max)
        self.logger.debug(f"Waiting {delay}s ...")
        time.sleep(delay)
    

def bind(
    mode: str, 
    input: Optional[str] = None,
    document_output: Type[Document] = Document,
    document_input: Optional[Type[Document]] = None
) -> Callable:
    def decorator(func: Callable) -> Callable:
        Scraper.mode_manager.register(mode, func, input, document_output, document_input)
        return func
    return decorator


def scrape(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> ModeResult:
        if not isinstance(self, Scraper):
            raise TypeError(f"The @scrape decorator can only be used in a class inheriting from Scraper, not in {type(self).__name__}")

        self.mode_manager.validate(self.mode)

        try:
            self.logger.debug(f"Running scraper mode \"{self.mode}\"")
            self.open()

            mode_info = self.mode_manager.get_mode(self.mode)
            if mode_info.func is None:
                raise ValueError(f"No function associated with mode '{self.mode}'")

            method = mode_info.func.__get__(self, type(self))
            document_output = mode_info.document_output
            document_input = mode_info.document_input

            results = []
            
            if (input_file := mode_info.input):
                input_list = self.read(filename=input_file)

                for d in input_list:
                    if document_input:
                        listing = self.create_document(obj=d, document=document_input)
                    else:
                        raise ValueError("Missing document_input parameter")
                        
                    self.logger.debug(f"Processing {listing}")

                    result = method(listing, *args, **kwargs)

                    if result:
                        results += result if isinstance(result, list) else [result]
                    self.wait(1, 2)
            else:
                results = method(*args, **kwargs)
                results = results if isinstance(results, list) else [results]

            self.save(links=results, document_output=document_output)
            return ModeResult(status=ModeStatus.SUCCESS)

        except Exception as e:
            return ModeResult(status=ModeStatus.ERROR, message=str(e))
        finally:
            self.close()

    return wrapper
