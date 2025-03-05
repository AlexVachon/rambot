import json
import time 
import random
import argparse

from functools import wraps


from botasaurus_driver.driver import Element, Driver


from ..logging_config import update_logger_config, get_logger

from .models import Document, ScraperModeManager, ModeResult, ModeStatus, Mode

from .config import ScraperConfig, ErrorConfig

from .exceptions import DriverError
from .decorators import no_print, errors

import typing


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
        self._driver: typing.Optional[Driver] = None
        
        self.logger = get_logger(__name__)
        
        self.setup()


    def setup(self) -> None:
        parser = argparse.ArgumentParser(description="Launch script with a specific mode")
        parser.add_argument("--mode", type=str, required=True, help="Scraper's mode to start")
        parser.add_argument("--url", type=str, required=False, help="URL to scrape (optional)")
        
        self.args = parser.parse_args()
        
        self.mode_manager.validate(self.args.mode)
        self.mode = self.args.mode
        
        self.setup_logging(mode=self.mode_manager.get_mode(self.mode))
        
        
    def setup_logging(self, mode: Mode):
        update_logger_config(log_to_file=True, file_path=mode.logs_output) if mode.save_logs else update_logger_config(log_to_file=False)
        
        
    def run(self) -> typing.List[Document]:
        if not hasattr(self, "args") or not hasattr(self.args, "mode"):
            raise RuntimeError("Calling .run() without calling .setup() first")

        method = self.mode_manager.get_func(self.mode)
        
        decorated_method = scrape(method)

        return decorated_method(self)


    @property
    def driver(self) -> typing.Optional[Driver]:
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
        if self._driver is not None:
            self.logger.debug("Closing browser...")
            self._driver.close()
            self._driver = None


    @errors(**ERRORS_CONFIG)
    def save(
        self,
        links: typing.List[Document],
        mode_result: ModeResult
    ) -> None:
        try:
            formatted_data = [link.output() for link in links]
            
            self.write(data=formatted_data, mode_result=mode_result)
            self.logger.debug(f"Saved {len(formatted_data)} links")
        except Exception as e:
            self.logger.error(f"Failed to save links: {e}")
            raise


    @errors(**ERRORS_CONFIG)
    def write(
        self,
        data: typing.List[typing.Type[Document]],
        mode_result: ModeResult
    ) -> None:
        try:
            filename = f"{self.mode}.json"
            
            with open(filename, 'w') as file:
                json.dump({"data": data, "run_stats": {"status": mode_result.status.value, "message": mode_result.message}}, file, indent=4)
        
        except Exception as e:
            self.logger.warning(f"Failed to write data to {filename}: {e}")
            raise


    @errors(**ERRORS_CONFIG)
    def read(
        self, 
        filename: str
    ) -> typing.Dict[str, typing.List[Document]]:
        with open(filename, 'r') as file:
            return json.load(file)


    @errors(**ERRORS_CONFIG)
    def create_document(
        self, 
        obj: typing.Dict[str, typing.Any], 
        document: typing.Type[Document]
    ) -> Document:
        return document(**obj)

    
    @no_print
    @errors(**ERRORS_CONFIG)
    def get(
        self, 
        url: str, 
        bypass_cloudflare: bool = False,
        accept_cookies: bool = False, 
        wait: typing.Optional[int] = None
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
    ) -> typing.List[Element]:
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
    input: typing.Optional[str] = None,
    document_input: typing.Optional[typing.Type[Document]] = None,
    save_logs: bool = False,
    logs_output: typing.Optional[str] = None,
    path: str = "."
    
) -> typing.Callable:
    def decorator(func: typing.Callable) -> typing.Callable:
        Scraper.mode_manager.register(
            mode, 
            func, 
            input, 
            document_input,
            save_logs,
            logs_output,
            path
        )
        return func
    return decorator


def scrape(func: typing.Callable) -> typing.Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> typing.List[Document]:
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
            document_input = mode_info.document_input

            results = []
            
            if (input_file := mode_info.input):
                input_list = {"data": [document_input(link=url).output()]} if (url := self.args.url) else self.read(filename=input_file)

                for d in input_list.get("data", []):
                    if document_input:
                        doc = self.create_document(obj=d, document=document_input)
                    else:
                        raise ValueError("Missing document_input parameter")
                        
                    self.logger.debug(f"Processing {doc}")

                    result = method(doc, *args, **kwargs)

                    if result:
                        result = result if isinstance(result, list) else [result]
                        
                        if not all(isinstance(r, Document) for r in result):
                            raise TypeError(f"Expected List[Document], but got {type(result)}")

                        results += result
                    self.wait(1, 2)
            else:
                results = method(*args, **kwargs)
                
                results = results if isinstance(results, list) else [results]

                if not all(isinstance(r, Document) for r in results):
                    raise TypeError(f"Expected List[Document], but got {type(results)} with elements {results}")
            
            mode_result = ModeResult(status=ModeStatus.SUCCESS.value)

        except Exception as e:
            results = []
            mode_result =  ModeResult(status=ModeStatus.ERROR.value, message=str(e))
        finally:
            self.logger.debug(f"Run is {mode_result.status.value} {mode_result.message if mode_result.message else ''}")
            
            self.save(links=results, mode_result=mode_result)
            self.close()
            
            return results

    return wrapper