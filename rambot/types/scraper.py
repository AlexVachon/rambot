from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Callable, Type, Union, Any

from botasaurus_driver.driver import Element, Wait, Driver
from ..scraper.models import Document, ScrapedDocument, Mode


class IScraper(ABC):
    """Interface for a web scraper with browser automation, request interception, 
    and multi-mode operation.
    """

    # ---- Proxy ----
    @abstractmethod
    def proxy_port(self) -> Union[str, int]:
        """Return the proxy port used by the scraper."""

    @abstractmethod
    def proxy_host(self) -> str:
        """Return the proxy host used by the scraper."""

    @abstractmethod
    def proxy(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        include_scheme: bool = False,
        use_https_scheme: bool = False
    ) -> Dict[str, str]:
        """Return a proxy dictionary compatible with `requests` or browser settings."""

    # ---- Setup ----
    @abstractmethod
    def setup(self) -> None:
        """Parse CLI arguments, validate mode, and configure logging."""

    @abstractmethod
    def setup_exception_handler(self, must_raise_exceptions: List[Type[Exception]] = [Exception]) -> None:
        """Configure exception handler with a list of exceptions to raise immediately."""

    @abstractmethod
    def setup_driver_config(self, **kwargs) -> None:
        """Configure the browser driver with default or custom options."""

    @abstractmethod
    def update_driver_config(self, **kwargs) -> None:
        """Update scraper configuration after initialization."""

    @abstractmethod
    def setup_logging(self, mode: Mode) -> None:
        """Initialize logging based on the scraper mode."""

    # ---- Run ----
    @abstractmethod
    def run(self) -> List[Document]:
        """
        Execute the scraping process based on the mode specified in CLI arguments.

        Starts the request interceptor, runs the appropriate mode function,
        and stops the interceptor when done.
        """

    # ---- Browser ----
    @property
    @abstractmethod
    def driver(self) -> Optional["Driver"]:
        """Return the browser driver, opening it if necessary."""

    @abstractmethod
    def open_browser(self, wait: bool = True) -> None:
        """Launch the browser with the configured settings."""

    @abstractmethod
    def close_browser(self) -> None:
        """Close the browser if it is running."""

    # ---- Navigation ----
    @abstractmethod
    def load_page(self, url: str, bypass_cloudflare: bool = False, accept_cookies: bool = False, wait: Optional[int] = None) -> None:
        """Load a page in the browser, optionally bypassing Cloudflare or accepting cookies."""

    @abstractmethod
    def get_current_url(self) -> str:
        """Return the current page URL."""

    @abstractmethod
    def refresh_page(self) -> None:
        """Reload the current page."""

    @abstractmethod
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript in the current page context."""

    @abstractmethod
    def navigate_back(self) -> None:
        """Go back to the previous page."""

    @abstractmethod
    def navigation_forward(self) -> None:
        """Go forward to the next page."""

    # ---- Elements ----
    @abstractmethod
    def select_all(self, selector: str, timeout: int = 10) -> List[Element]:
        """Select all matching elements."""

    @abstractmethod
    def select(self, selector: str, timeout: int = 10) -> Element:
        """Select a single element."""

    @abstractmethod
    def click(self, selector: str, wait: Optional[int] = Wait.SHORT):
        """Click an element."""

    @abstractmethod
    def is_element_visible(self, selector: str, wait: Optional[int] = Wait.SHORT) -> bool:
        """Return True if the element is visible."""

    # ---- Storage ----
    @abstractmethod
    def get_cookies(self) -> List[dict]:
        """Return cookies from the browser."""

    @abstractmethod
    def add_cookies(self, cookies: List[dict]) -> None:
        """Add cookies to the browser."""

    @abstractmethod
    def delete_cookies(self) -> None:
        """Delete all cookies."""

    @abstractmethod
    def get_local_storage(self) -> dict:
        """Return localStorage data."""

    @abstractmethod
    def add_local_storage(self, local_storage: dict) -> None:
        """Add items to localStorage."""

    @abstractmethod
    def delete_local_storage(self) -> None:
        """Clear localStorage."""

    # ---- Scroll ----
    @abstractmethod
    def scroll(self, selector: Optional[str] = None, by: int = 1000, smooth_scroll: bool = True, wait: Optional[int] = Wait.SHORT) -> None:
        """Scroll the page or an element."""

    @abstractmethod
    def scroll_to_bottom(self, selector: Optional[str] = None, smooth_scrolling: bool = True, wait: Optional[int] = Wait.SHORT) -> None:
        """Scroll to the bottom of the page or element."""

    @abstractmethod
    def scroll_to_element(self, selector: str, wait: Optional[int] = Wait.SHORT) -> None:
        """Scroll to bring an element into view."""

    # ---- Requests ----
    @abstractmethod
    def get_requests(self) -> List[dict]:
        """Return captured HTTP requests."""

    # ---- Utils ----
    @abstractmethod
    def wait(self, min: float = 0.1, max: float = 1) -> None:
        """Sleep for a random time between min and max seconds."""

    @abstractmethod
    def save(self, links: List[ScrapedDocument]) -> None:
        """Save scraped documents to a file."""

    @abstractmethod
    def write(self, data: List[ScrapedDocument]) -> None:
        """Write scraped data to disk."""

    @abstractmethod
    def read(self, filename: str) -> Dict[str, List[Document]]:
        """Read saved scraped data from disk."""

    @abstractmethod
    def create_document(self, obj: Dict[str, Any], document: Type[Document]) -> Document:
        """Create a Document instance from a dictionary."""