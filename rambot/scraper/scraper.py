import os
import json
import time 
import random
import argparse

from functools import wraps

from botasaurus_driver.driver import Element, Driver, Wait

from ..helpers import helpers

from .interceptor import start_mitmproxy, stop_mitmproxy
from .interceptor.interceptor import get_requests

from ..logging_config import update_logger_config, get_logger

from .models import Document, ScraperModeManager, Mode, ScrapedDocument
from .exception_handler import ExceptionHandler

from .config import ScraperConfig

from .exceptions import DriverError
from .decorators import no_print

import typing


class Scraper:
    """
    A class for scraping data from websites using a configurable browser and various scraping modes.

    The `Scraper` class facilitates the configuration of a scraping session, including setting up the browser, logging, proxies, and mode-based operations. It integrates exception handling, allows custom configurations, and supports interacting with web elements such as clicking, selecting, and scrolling. Additionally, it manages data storage, including saving and loading scraped data, and supports proxy configuration.

    Attributes:
        mode_manager (ScraperModeManager): Manages different scraper modes and their associated functions.
        logger (Logger): The logger used for recording information and errors during the scraping process.
        config (ScraperConfig): The configuration settings for the scraper instance.
        exception_handler (ExceptionHandler): Handles exceptions during the scraping process.
    """
    
    mode_manager = ScraperModeManager()


    def __init__(self):        
        self._driver: typing.Optional[Driver] = None
        self.logger = get_logger(__name__)
        
        self.setup()
        
        self.setup_driver_config()
        self.setup_exception_handler()
    

    """
        PROXY FONCTIONS
    """

    def proxy_port(self) -> typing.Union[str, int]:
        return "8080"
    
 
    def proxy_host(self) -> str:
        return "localhost"
    

    def proxy(
        self,
        username: typing.Optional[str] = None, 
        password: typing.Optional[str] = None, 
        include_scheme: bool = False, 
        use_https_scheme: bool = False
    ) -> typing.Dict[str, str]:
        
        return helpers.get_proxies(
            host=self.proxy_host(),
            port=self.proxy_port(),
            username=username, 
            password=password, 
            include_scheme=include_scheme, 
            use_https_scheme=use_https_scheme
        )


    def setup(self) -> None:
        parser = argparse.ArgumentParser(description="Launch script with a specific mode")
        parser.add_argument("--mode", type=str, required=True, help="Scraper's mode to start")
        parser.add_argument("--url", type=str, required=False, help="URL to scrape (optional)")
        
        self.args = parser.parse_args()
        
        self.mode_manager.validate(self.args.mode)
        self.mode = self.args.mode
        
        self.setup_logging(mode=self.mode_manager.get_mode(self.mode))
    
    
    def setup_exception_handler(self, must_raise_exceptions: typing.List[typing.Type[Exception]] = [Exception]) -> None:
        """
        Dynamically configure the exception handler with the list of exceptions to raise.
        """
        self.exception_handler = ExceptionHandler(must_raise_exceptions=must_raise_exceptions)
    
    
    def setup_driver_config(self, **kwargs):
        """Configure the driver with default parameters, but allows modifications."""
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
        """Update the scraper configuration after initialization."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                self.logger.warning(f"Unknown configuration key: {key}")

    
    def setup_logging(self, mode: Mode):
        update_logger_config(class_name=self.__class__.__name__, log_to_file=True, file_path=mode.log_file_name) if mode.enable_file_logging else update_logger_config(class_name=self.__class__.__name__, log_to_file=False)
        
        
    def run(self) -> typing.List[Document]:
        """
        Executes the scraping process based on the mode specified in the command-line arguments.

        This function depends on the "--mode" argument passed in the `launch.json` configuration. 
        It initializes and runs `mitmproxy`, retrieves the appropriate scraping method using 
        `mode_manager.get_func(self.mode)`, applies the `scrape` decorator, and executes the 
        decorated method.

        Returns:
            list[Document]: A list of extracted documents.

        Raises:
            RuntimeError: If called without first executing `.setup()`.
            Exception: Any unexpected errors are handled by `self.exception_handler.handle(e)`.
        """
        try:
            if not hasattr(self, "args") or not hasattr(self.args, "mode"):
                raise RuntimeError("Calling .run() without calling .setup() first")

            start_mitmproxy(proxy_port=self.proxy_port())

            method = self.mode_manager.get_func(self.mode)
            
            decorated_method = scrape(method)

            result = decorated_method(self)
            stop_mitmproxy()
            
            return result
        except Exception as e:
            self.exception_handler.handle(e)


    @property
    def driver(self) -> typing.Optional[Driver]:
        if not hasattr(self, '_driver') or not self._driver:
            self.open_browser()
        return self._driver


    @no_print
    def open_browser(
        self, 
        wait: bool = True
    ) -> None:
        try:
            self.logger.debug("Opening browser ...")
            
            driver_config = {
                "headless": self.config.headless,
                "proxy": self.config.proxy,
                "profile": self.config.profile,
                "tiny_profile": self.config.tiny_profile,
                "block_images": self.config.block_images,
                "block_images_and_css": self.config.block_images_and_css,
                "wait_for_complete_page_load": wait,
                "extensions": self.config.extensions,
                "arguments": self.config.arguments if self.config.arguments else [
                    "--ignore-certificate-errors",
                    "--ignore-ssl-errors=yes"
                ],
                "user_agent": self.config.user_agent,
                "lang": self.config.lang,
                "beep": self.config.beep,
            }
            self._driver = Driver(**driver_config)
            
            if not self._driver._tab:
                raise DriverError("Can't initialize driver")
            
        except Exception as e:
            self.exception_handler.handle(e)
        
        
    @no_print
    def close_browser(self) -> None:
        try:
            if self._driver is not None:
                self.logger.debug("Closing browser...")
                self._driver.close()
                self._driver = None
        except Exception as e:
            self.exception_handler.handle(e)
            


    """
        NAVIGATION FUNCTIONS
    """

    @no_print
    def load_page(
        self, 
        url: str, 
        bypass_cloudflare: bool = False,
        accept_cookies: bool = False, 
        wait: typing.Optional[int] = None
    ) -> None:
        try:
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
        except Exception as e:
            self.exception_handler.handle(e)
    
    
    def get_current_url(self) -> str:
        try:
            return self.driver.current_url
        except Exception as e:
            self.exception_handler.handle(e)
    
    
    def refresh_page(self) -> None:
        try:
            self.driver.reload()
        except Exception as e:
            self.exception_handler.handle(e)
          
    
    def execute_script(self, script: str) -> typing.Any:
        try:
            return self.driver.run_js(script)
        except Exception as e:
            self.exception_handler.handle(e)
    
    
    def navigate_back(self) -> None:
        self.execute_script(script="window.history.back()")
    
    
    def navigation_forward(self) -> None:
        self.execute_script(script="window.history.forward()")
    
          
    """
        ELEMENT FUNCTIONS
    """
    
    def select_all(
        self, 
        selector: str, 
        timeout: int = 10
    ) -> typing.List[Element]:
        return self.driver.select_all(
            selector=selector,
            wait=timeout
        )
    
    
    def select(
        self, 
        selector: str, 
        timeout: int = 10
    ) -> Element:
        return self.driver.select(
            selector=selector,
            wait=timeout
        )
        
    
    def click(
        self,
        selector: str,
        wait: typing.Optional[int] = Wait.SHORT
    ):
        self.driver.click(selector, wait)
        
    
    def is_element_visible(
        self, 
        selector: str, 
        wait: typing.Optional[int] = Wait.SHORT
    ) -> bool:
        return self.driver.is_element_present(selector, wait)
    
    
    
    """
        STORAGE FUNCTIONS
    """
    
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


    """
        SCROLL FUNCTIONS
    """

    def scroll(
        self,
        selector: typing.Optional[str] = None,
        by: int = 1000,
        smooth_scroll: bool = True,
        wait: typing.Optional[int] = Wait.SHORT
    ) -> None:
        self.driver.scroll(selector, by, smooth_scroll, wait)
    
    
    def scroll_to_bottom(
        self,
        selector: typing.Optional[str] = None,
        smooth_scrolling: bool = True,
        wait: typing.Optional[int] = Wait.SHORT
    ) -> None:
        self.driver.scroll_to_bottom(selector, smooth_scrolling, wait)


    def scroll_to_element(
        self, 
        selector: str, 
        wait: typing.Optional[int] = Wait.SHORT
    ) -> None:
        self.driver.scroll_into_view(selector, wait)


    
    """
        REQUESTS FUNCTIONS
    """

    def get_requests(self):
        return get_requests()


    """
        UTILS FUNCTIONS
    """
    
    def wait(
        self, 
        min: float = 0.1, 
        max: float = 1
    ) -> None:
        delay = random.uniform(min, max)
        self.logger.debug(f"Waiting {delay}s ...")
        time.sleep(delay)
        
        
    def save(
        self,
        links: typing.List[ScrapedDocument]
    ) -> None:
        try:
            self.write(data=links)
            self.logger.debug(f"Saved {len(links)} links")
        except Exception as e:
            self.exception_handler.handle(e)


    def write(
        self,
        data: typing.List[ScrapedDocument]
    ) -> None:
        try:
            filename = f"{self.mode}.json"
            
            with open(filename, 'w') as file:
                json.dump(
                    [d.to_dict() for d in data], 
                    file, 
                    indent=4
                )
        
        except Exception as e:
            self.exception_handler.handle(e)


    def read(
        self, 
        filename: str
    ) -> typing.Dict[str, typing.List[Document]]:
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except Exception as e:
            self.exception_handler.handle(e)


    def create_document(
        self, 
        obj: typing.Dict[str, typing.Any], 
        document: typing.Type[Document]
    ) -> Document:
        try:
            return document(**obj.get("document", {}))
        except Exception as e:
            self.exception_handler.handle(e)
        
        

"""
Scraper decorators
"""
def bind(
    mode: str, 
    input: typing.Optional[typing.Union[str, typing.Callable[[], typing.List[typing.Dict[str, typing.Any]]]]] = None,
    save: typing.Optional[typing.Callable[[typing.Any], None]] = None,
    document_input: typing.Optional[typing.Type[Document]] = None,
    enable_file_logging: bool = True,
    log_file_name: typing.Optional[str] = None,
    log_directory: str = "."
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
        enable_file_logging (bool): Whether to enable logging for this mode.
        log_file_name (Optional[str]): The output path for logs. If None, a default path is used.
        log_directory (str): The directory path where logs should be stored. Defaults to the current directory.

    Returns:
        Callable: The original function, now registered as a mode.

    Example:
        ```python
        @bind(mode="extract_data", save=my_save_function, log_directory="logs/mode_cities")
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
            enable_file_logging,
            log_file_name,
            log_directory
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
        try:
            self.mode_manager.validate(self.mode)
            
            mode_info = self.mode_manager.get_mode(self.mode)
            if mode_info.func is None:
                raise ValueError(f"No function associated with mode '{self.mode}'")

            method = mode_info.func.__get__(self, type(self))
            document_input = mode_info.document_input
            save = mode_info.save


            self.logger.debug(f"Running scraper mode \"{self.mode}\"")
            self.open_browser()

            results = set()

            if (input_file := mode_info.input):
                if callable(input_file):
                    input_list = input_file(self)
                else:
                    input_list = [
                        ScrapedDocument.from_document(
                            document=document_input(link=url), 
                            source=self.__class__.__name__, 
                            mode="restaurant_details"
                        ).to_dict()
                    ] if (url := self.args.url) else self.read(filename=input_file)

                for d in input_list:
                    if document_input:
                        doc = self.create_document(obj=d, document=document_input)

                    self.logger.debug(f"Processing {doc}")

                    try:
                        result = method(doc, *args, **kwargs)

                        if result:
                            if not isinstance(result, list): result = [result]
                            if not all(isinstance(r, Document) for r in result):
                                raise TypeError(f"Expected List[Document], but got {type(result)} with elements {result}")

                            results.update(result)
                    except Exception as e:
                        self.logger.error(f"Error processing {doc}: {str(e)}")

                    self.wait(1, 2)
            else:
                result = method(*args, **kwargs)
                if not isinstance(result, (list, set)):
                    result = {result}
                else:
                    result = set(result)

                if not all(isinstance(r, Document) for r in result):
                    raise TypeError(f"Expected List[Document], but got {type(result)} with elements {result}")

                results.update(result)
        except Exception as e:
            results = set()
            self.exception_handler.handle(e)
        finally:
            if save is not None:
                save(self, list(results))

            self.save(links=list([ScrapedDocument.from_document(document=r, mode=self.mode, source=self.__class__.__name__) for r in results]))
            self.close_browser()

            return list(results)

    return wrapper