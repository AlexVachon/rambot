#botminator/scraper.py
import os
import json
import time 
import random

from functools import wraps

from botasaurus.browser import Driver

from botasaurus_driver.driver import Element

from .models import Listing, Restaurant, ScraperModeManager
from .config import ScraperConfig, ErrorConfig
from .exceptions import DriverError

from .decorators import no_print, errors

from typing import Optional, List, Dict, Any, Union, Literal
from datetime import datetime


from loguru import logger as default_logger

logger = default_logger


class Scraper:
    
    ERRORS_CONFIG: ErrorConfig = {
        "must_raise": lambda self: self.config.must_raise,
        "create_logs": lambda self: self.config.create_error_logs
    }
    
    
    def __init__(self, config: ScraperConfig = None):
        
        ScraperModeManager.add_mode("restaurant_details")
        ScraperModeManager.add_mode("restaurant_links")
        
        self.config = config or ScraperConfig()
        self._driver: Optional[Driver] = None
        self.logger = logger
        
        for mode in ScraperModeManager.get_modes():
            ScraperModeManager.validate_mode(mode)


    @property
    def driver(self) -> Optional[Driver]:
        if not hasattr(self, '_driver') or not self._driver:
            self.open()
        return self._driver


    @no_print
    @errors(**ERRORS_CONFIG)
    def open(self, wait: bool = True) -> None:
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


    @no_print
    @errors(**ERRORS_CONFIG)
    def get(self, url: str, bypass_cloudflare: bool = False,
                 accept_cookies: bool = False, wait: Optional[int] = None) -> None:
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
    def find_all(self, selector: str, timeout: int = 10) -> Optional[List[Element]]:
        return self.driver.select_all(
            selector=selector,
            wait=timeout
        )
    
    
    @no_print
    @errors(**ERRORS_CONFIG)
    def find(self, selector: str, timeout: int = 10) -> Optional[Element]:
        return self.driver.select(
            selector=selector,
            wait=timeout
        )
    
    
    @errors(**ERRORS_CONFIG)
    def save(self, links: List[str], mode: str = "") -> None:
        try:
            listing_links: List[Listing] = [self.create_listing({"link": link}).model_dump() for link in links]
            
            self.write(data=listing_links, mode=mode)
            self.logger.debug(f"Saved {len(listing_links)} links")
            
        except Exception as e:
            self.logger.error(f"Failed to save links: {e}")
            raise


    @errors(**ERRORS_CONFIG)
    def write(self, data: List[Listing], mode: str = "") -> None:
        try:

            if mode:
                ScraperModeManager.validate_mode(mode)

            filename = f"{mode}.json"
            
            os.makedirs("output", exist_ok=True)
            
            path = os.path.join('output', filename)
            
            with open(path, 'w') as file:
                json.dump({"data": data}, file, indent=4)
            
            self.logger.debug("Data saved")
            
        except Exception as e:
            self.logger.warning(f"Failed to write data to {path}: {e}")
            raise

    
    @errors(**ERRORS_CONFIG)
    def read(self, filename: str) -> Dict[str, List[Listing]]:
        with open(filename, 'r') as file:
            return json.load(file)
    
    
    @errors(**ERRORS_CONFIG)
    def create_listing(self, data: Dict[str, Any]) -> Listing:
        return Listing(**data)
    
    
    @errors(**ERRORS_CONFIG)
    def wait(self, min: float = 0.1, max: float = 1):
        delay = random.uniform(min, max)
        self.logger.debug(f"waiting {delay:.2}s ...")
        time.sleep(delay)
        
    
    @errors(**ERRORS_CONFIG)
    def get_detail_links(self, listing: Listing) -> List[str]:
        raise NotImplementedError("You must implement get_detail_links")
    
    
    @errors(**ERRORS_CONFIG)
    def get_details(self, listing: Listing) -> Restaurant:
        raise NotImplementedError("You must implement get_details")
    

def scraper(mode: str, input: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            ScraperModeManager.validate_mode(mode)
            try:
                self.logger.debug(f"Running scraper mode \"{mode}\"")

                results = []
                links = self.read(filename=input)
                
                self.open()
                
                for link in links:
                    listing: Listing = self.create_listing(data=link)
                    self.logger.debug(f"Scraping {listing}")
                    
                    result = func(self, listing, *args, **kwargs)
                    if result:
                        results += result if isinstance(result, list) else [result]
                    
                    self.wait(1,2)
                    
                self.save(links=results, mode=mode)
            finally:
                self.close()
        return wrapper
    return decorator