import json
import time 
import random
import argparse

from functools import wraps

from botasaurus_driver.driver import Element, Driver, Wait

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
            formatted_data = [link.to_dict() for link in links]
            
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
    
    
    def get_current_url(self) -> str:
        return self.driver.current_url
    
    
    def refresh(self) -> None:
        self.driver.reload()
        
        
    def find_all(
        self, 
        selector: str, 
        timeout: int = 10
    ) -> typing.List[Element]:
        return self.driver.select_all(
            selector=selector,
            wait=timeout
        )
    
    
    def find(
        self, 
        selector: str, 
        timeout: int = 10
    ) -> Element:
        return self.driver.select(
            selector=selector,
            wait=timeout
        )
    
    
    def wait(
        self, 
        min: float = 0.1, 
        max: float = 1
    ) -> None:
        delay = random.uniform(min, max)
        self.logger.debug(f"Waiting {delay}s ...")
        time.sleep(delay)

    
    def click(
        self,
        selector: str,
        element: typing.Optional[Element] = None,
        wait: typing.Optional[int] = Wait.SHORT
    ):
        element.click(selector, wait) if element else self.driver.click(selector, wait)
        
    
    def wait_element(
        self, 
        selector: str, 
        wait: typing.Optional[int] = Wait.SHORT
    ) -> bool:
        return self.driver.is_element_present(selector, wait)
    
    
    def get_cookies(self) -> typing.List[dict]:
        return self.driver.get_cookies()
    
    
    def add_cookies(
        self, 
        cookies: typing.List[dict]
    ) -> None:
        self.driver.add_cookies(cookies)
    
    
    def delete_cookies(self) -> None:
        self.driver.delete_cookies()


    def get_local_storage(self) -> dict:
        return self.driver.get_local_storage()


    def add_local_storage(
        self, 
        local_storage: dict
    ) -> None:
        self.driver.add_local_storage(local_storage)


    def delete_local_storage(self) -> None:
        self.driver.delete_local_storage()
        self.driver.element


    def navigate_back(self):
        pass


    def navigate_forward(self):
        pass
    
    
    def scroll(
        self,
        selector: typing.Optional[str] = None,
        by: int = 1000,
        smooth_scroll: bool = True,
        wait: typing.Optional[int] = Wait.SHORT
    ) -> None:
        self.driver.scroll(selector, by, smooth_scroll, wait)
    
    
    def scroll_bottom(
        self,
        selector: typing.Optional[str] = None,
        smooth_scrolling: bool = True,
        wait: typing.Optional[int] = Wait.SHORT
    ) -> None:
        self.driver.scroll_to_bottom(selector, smooth_scrolling, wait)


    def scroll_by(
        self, 
        selector: str, 
        wait: typing.Optional[int] = Wait.SHORT
    ) -> None:
        self.driver.scroll_into_view(selector, wait)


"""
Scraper decorators
"""
def bind(
    mode: str, 
    input: typing.Optional[typing.Union[str, typing.Callable[[], typing.List[typing.Dict[str, typing.Any]]]]] = None,
    save: typing.Optional[typing.Callable[[typing.Any], None]] = None,
    document_input: typing.Optional[typing.Type[Document]] = None,
    save_logs: bool = False,
    logs_output: typing.Optional[str] = None,
    path: str = "."
) -> typing.Callable:
    """
    A decorator to register a function as a mode in the ScraperModeManager.

    This decorator allows binding a function to a specific mode with optional input processing, 
    saving functionality, logging configuration, and document input type.

    Args:
        mode (str): The name of the mode to register.
        input (Optional[Union[str, Callable]]): The input source for the mode, which can be:
            - A string representing an input source.
            - A callable that returns a list of dictionaries.
        save (Optional[Callable[[Any], None]]): A function to save the results of the mode.
        document_input (Optional[Type[Document]]): The document type associated with this mode.
        save_logs (bool): Whether to enable logging for this mode.
        logs_output (Optional[str]): The output path for logs. If None, a default path is used.
        path (str): The directory path where logs should be stored. Defaults to the current directory.

    Returns:
        Callable: The original function, now registered as a mode.

    Example:
        ```python
        @bind(mode="extract_data", save=my_save_function, save_logs=True)
        def extract():
            return {"data": "example"}
        ```
    """
    def decorator(func: typing.Callable) -> typing.Callable:
        Scraper.mode_manager.register(
            mode, 
            func, 
            input,
            save,
            document_input,
            save_logs,
            logs_output,
            path
        )
        return func
    return decorator


def scrape(func: typing.Callable) -> typing.Callable:
    """
    A decorator for handling the scraping process in a class inheriting from Scraper.

    This decorator ensures that the function is executed within a properly managed scraping 
    session, including validation, logging, input handling, and saving results.

    Args:
        func (Callable): The function to be decorated, expected to process and return a list of `Document` objects.

    Returns:
        Callable: A wrapped function that manages the scraping process.

    Raises:
        TypeError: If the decorator is used on a class that does not inherit from `Scraper`.
        ValueError: If no function is associated with the current mode.
        TypeError: If the function does not return a list of `Document` instances.

    Functionality:
        - Validates that the `Scraper` class is being used.
        - Retrieves the mode's configuration from `ScraperModeManager`.
        - Processes input data, either from a callable or a file.
        - Calls the mode’s associated function, ensuring it returns a list of `Document` objects.
        - Handles logging and exceptions.
        - Saves the results using the mode's `save` function (if provided) and the scraper’s `save` method.

    Example:
        ```python
        class MyScraper(Scraper):
            @scrape
            def my_scraper_function(self, document: Document):
                # Process the document and return results
                return document
        ```
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> typing.List[Document]:
        if not isinstance(self, Scraper):
            raise TypeError(f"The @scrape decorator can only be used in a class inheriting from Scraper, not in {type(self).__name__}")

        self.mode_manager.validate(self.mode)

        try:
            self.logger.debug(f"Running scraper mode \"{self.mode}\"")
            self.open()

            mode_info = self.mode_manager.get_mode(self.mode)
            if mode_info.func is None: raise ValueError(f"No function associated with mode '{self.mode}'")

            method = mode_info.func.__get__(self, type(self))
            document_input = mode_info.document_input
            save = mode_info.save

            results = []
            
            if (input_file := mode_info.input):
                if callable(input_file): input_list = {"data": input_file(self)}
                else: input_list = {"data": [document_input(link=url).to_dict()]} if (url := self.args.url) else self.read(filename=input_file)

                for d in input_list.get("data", []):
                    
                    if document_input: doc = self.create_document(obj=d, document=document_input)
                        
                    self.logger.debug(f"Processing {doc}")

                    result = method(doc, *args, **kwargs)

                    if result:
                        result = result if isinstance(result, list) else [result]
                        if not all(isinstance(r, Document) for r in result): raise TypeError(f"Expected List[Document], but got {type(result)}")

                        results += result
                    self.wait(1, 2)
            else:
                results = method(*args, **kwargs)
                results = results if isinstance(results, list) else [results]

                if not all(isinstance(r, Document) for r in results): raise TypeError(f"Expected List[Document], but got {type(results)} with elements {results}")
            
            mode_result = ModeResult(status=ModeStatus.SUCCESS.value)

        except Exception as e:
            results = []
            mode_result =  ModeResult(status=ModeStatus.ERROR.value, message=str(e))
        finally:
            self.logger.debug(f"Run is {mode_result.status.value} {mode_result.message if mode_result.message else ''}")
            
            if save is not None: save(self, results, mode_result)
            
            self.save(links=results, mode_result=mode_result)
            self.close()
            
            return results

    return wrapper