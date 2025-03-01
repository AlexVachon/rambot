from botasaurus.browser import Driver
from botasaurus_driver.core.config import Config

from botasaurus_driver.driver import Element

from .config import ScraperConfig
from .exceptions import DriverError
from typing import Optional

import asyncio

class Scraper:
    def __init__(self, config: Config = None):
        """
        Initialise le scraper avec une configuration.
        
        Args:
            config: Dictionnaire de configuration optionnel
        """
        self.config = ScraperConfig(**(config or {}))
        self._driver: Optional[Driver] = None

    @property
    async def driver(self) -> Optional[Driver]:
        """
        Propriété asynchrone pour accéder au driver.
        
        Assure que le driver est initialisé avant son utilisation.
        """
        if not hasattr(self, '_driver') or not self._driver:
            await self.open()
        return self._driver

    async def open(self, wait: bool = True) -> None:
        """
        Initialise le driver avec la configuration et affiche le navigateur.
        
        Args:
            wait: Attendre le chargement complet de la page
        """
        try:
            driver_config = {
                "headless": False,
                "proxy": "http://proxy.brizodata.com:24182",
                # "profile": None,
                # "tiny_profile": False,
                # "block_images": False,
                # "block_images_and_css": False,
                # "wait_for_complete_page_load": wait,
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
                
            await asyncio.sleep(2)
            
        except Exception as e:
            raise DriverError(f"Erreur lors de l'initialisation du driver: {str(e)}")

    async def close(self) -> None:
        try:
            if self._driver is not None:
                self._driver.close()
                self._driver = None
        except Exception as e:
            raise DriverError(f"Couldn't close driver: {str(e)}")

    async def get(self, url: str, bypass_cloudflare: bool = False,
                 accept_cookies: bool = False, wait: Optional[int] = None) -> None:
        driver = await self.driver
        try:
            if driver.config.is_new:
                async def async_google_get(*args, **kwargs):
                    return driver.google_get(*args, **kwargs)
                
                await async_google_get(
                    link=url,
                    bypass_cloudflare=bypass_cloudflare,
                    accept_google_cookies=accept_cookies,
                    wait=wait or self.config.min_delay
                )
            else:
                response = driver.requests.get(url=url)
                response.raise_for_status()
                return response
                
        except Exception as e:
            raise DriverError(f"Erreur lors du chargement de la page: {str(e)}")

    async def find(self, selector: str, timeout: int = 10) -> Optional[Element]:
        driver = await self.driver
        try:
            return driver.select(
                selector=selector,
                wait=min(timeout, self.config.max_delay)
            )
        except Exception as e:
            raise DriverError(f"Erreur lors de la recherche d'éléments: {str(e)}")