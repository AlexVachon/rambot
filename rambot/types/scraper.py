from abc import ABC, abstractmethod

from typing import Optional, List, Dict, Type, Union, Any

from botasaurus_driver.driver import Wait

from .html import IHTML
from ..scraper.models import Document, ScrapedDocument, Mode, ScraperModeManager
from ..browser.driver import Driver


class IScraper(ABC):
    """Interface for a web scraper with browser automation, request interception, 
    and multi-mode operation.
    """

    mode_manager: ScraperModeManager
    _driver: Optional[Driver] = None
    _html: Optional[IHTML] = None

    # ---- Proxy ----
    @abstractmethod
    def proxy_port(self) -> Union[str, int]:
        """Return the proxy port used by the scraper."""
        pass

    @abstractmethod
    def proxy_host(self) -> str:
        """Return the proxy host used by the scraper."""
        pass

    @abstractmethod
    def proxy(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        include_scheme: bool = False,
        use_https_scheme: bool = False
    ) -> Dict[str, str]:
        """Return a proxy dictionary compatible with `requests` or browser settings."""
        pass

    # ---- Setup ----
    @abstractmethod
    def setup(self) -> None:
        """Parse CLI arguments, validate mode, and configure logging."""
        pass

    @abstractmethod
    def setup_exception_handler(self, must_raise_exceptions: List[Type[Exception]] = [Exception]) -> None:
        """Configure exception handler with a list of exceptions to raise immediately."""
        pass

    @abstractmethod
    def setup_driver_config(self, **kwargs) -> None:
        """Configure the browser driver with default or custom options."""
        pass

    @abstractmethod
    def update_driver_config(self, **kwargs) -> None:
        """Update scraper configuration after initialization."""
        pass

    @abstractmethod
    def setup_logging(self, mode: Mode) -> None:
        """Initialize logging based on the scraper mode."""
        pass

    # ---- Run ----
    @abstractmethod
    def run(self) -> List[Document]:
        """
        Execute the scraping process based on the mode specified in CLI arguments.

        Starts the request interceptor, runs the appropriate mode function,
        and stops the interceptor when done.
        """
        pass

    # ---- Browser ----
    @property
    @abstractmethod
    def driver(self) -> Optional["Driver"]:
        """Return the browser driver, opening it if necessary."""
        pass

    @abstractmethod
    def open_browser(self, wait: bool = True) -> None:
        """Launch the browser with the configured settings."""
        pass

    @abstractmethod
    def close_browser(self) -> None:
        """Close the browser if it is running."""
        pass

    # ---- Navigation ----
    @abstractmethod
    def load_page(self, url: str, bypass_cloudflare: bool = False, accept_cookies: bool = False, wait: Optional[int] = None, timeout: Optional[int] = 5) -> None:
        """Load a page in the browser, optionally bypassing Cloudflare or accepting cookies."""
        pass

    @abstractmethod
    def get_current_url(self) -> str:
        """Return the current page URL."""
        pass

    @abstractmethod
    def refresh_page(self) -> None:
        """Reload the current page."""
        pass

    @abstractmethod
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript in the current page context."""
        pass

    @abstractmethod
    def navigate_back(self) -> None:
        """Go back to the previous page."""
        pass

    @abstractmethod
    def navigation_forward(self) -> None:
        """Go forward to the next page."""
        pass

    # ---- Elements ----
    @property
    @abstractmethod
    def html(self) -> IHTML:
        """Return the HTML interface for element interaction."""
        pass

    # ---- Storage ----
    @abstractmethod
    def get_cookies(self) -> List[dict]:
        """Return cookies from the browser."""
        pass

    @abstractmethod
    def add_cookies(self, cookies: List[dict]) -> None:
        """Add cookies to the browser."""
        pass

    @abstractmethod
    def delete_cookies(self) -> None:
        """Delete all cookies."""
        pass

    @abstractmethod
    def get_local_storage(self) -> dict:
        """Return localStorage data."""
        pass

    @abstractmethod
    def add_local_storage(self, local_storage: dict) -> None:
        """Add items to localStorage."""
        pass

    @abstractmethod
    def delete_local_storage(self) -> None:
        """Clear localStorage."""
        pass

    # ---- Scroll ----
    @abstractmethod
    def scroll(self, selector: Optional[str] = None, by: int = 1000, smooth_scroll: bool = True, wait: Optional[int] = Wait.SHORT) -> None:
        """Scroll the page or an element."""
        pass

    @abstractmethod
    def scroll_to_bottom(self, selector: Optional[str] = None, smooth_scrolling: bool = True, wait: Optional[int] = Wait.SHORT) -> None:
        """Scroll to the bottom of the page or element."""
        pass

    @abstractmethod
    def scroll_to_element(self, selector: str, wait: Optional[int] = Wait.SHORT) -> None:
        """Scroll to bring an element into view."""
        pass


    # ---- Utils ----
    @abstractmethod
    def sleep(self, t: Optional[float]) -> None:
        """Sleep for a specified time in seconds."""
        pass

    @abstractmethod
    def wait(self, min: float = 0.1, max: float = 1) -> None:
        """Sleep for a random time between min and max seconds."""
        pass

    @abstractmethod
    def save(self, links: List[ScrapedDocument]) -> None:
        """Save scraped documents to a file."""
        pass

    @abstractmethod
    def write(self, data: List[ScrapedDocument]) -> None:
        """Write scraped data to disk."""
        pass

    @abstractmethod
    def read(self, filename: str) -> Dict[str, List[Document]]:
        """Read saved scraped data from disk."""
        pass

    @abstractmethod
    def create_document(self, obj: Dict[str, Any], document: Type[Document]) -> Document:
        """Create a Document instance from a dictionary."""
        pass