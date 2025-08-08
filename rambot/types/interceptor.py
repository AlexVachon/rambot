import os
import tempfile

from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Dict, Any

from .scraper import IScraper
from .request import Request


class IInterceptor(ABC):
    """Interface for a request interceptor used in web scraping."""

    _scraper: "IScraper"
    _requests_path: str

    def __init__(self, scraper: IScraper) -> None:
        """
        Initialize the interceptor with a scraper instance.

        Args:
            scraper (IScraper): The scraper instance to use.
        """
        self._scraper = scraper
        self.logger = scraper.logger
        self._requests_path = os.path.join(
            tempfile.gettempdir(),
            f"__{self._scraper.__class__.__name__.lower()}_requests.json"
        )

    @abstractmethod
    def start(self) -> None:
        """
        Start the request interceptor to capture network requests.
        Typically launches a proxy like mitmproxy in a subprocess.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the request interceptor and clean up any resources
        (such as temporary files or background processes).
        """
        pass

    @abstractmethod
    def requests(self) -> List[Request]:
        """
        Retrieve all captured requests as a list of Request objects.

        Returns:
            List[Request]: Parsed request objects.
        """
        pass

    @abstractmethod
    def filter_by_url(self, keyword: str, requests: Optional[List[Request]] = None, case_sensitive: bool = False) -> List[Request]:
        """Return requests with URLs containing the keyword."""
        pass

    @abstractmethod
    def filter_by_method(self, method: str, requests: Optional[List[Request]] = None) -> List[Request]:
        """Return requests matching HTTP method (case-insensitive)."""
        pass

    @abstractmethod
    def filter_by_status_code(self, status_codes: List[int], requests: Optional[List[Request]] = None) -> List[Request]:
        """Return requests whose response status code is in the given list."""
        pass

    @abstractmethod
    def filter_by_header(self, header_name: str, header_value: Optional[str] = None, requests: Optional[List[Request]] = None, case_sensitive: bool = False) -> List[Request]:
        """Return requests where the specified header matches (optionally by value)."""
        pass

    @abstractmethod
    def filter_by_response_encoding(self, encoding: str, requests: Optional[List[Request]] = None) -> List[Request]:
        """Return requests where response encoding matches the given encoding."""
        pass

    @abstractmethod
    def find_first(self, predicate: Callable[[Request], bool], requests: Optional[List[Request]] = None) -> Optional[Request]:
        """Find the first request matching the given predicate."""
        pass

    @abstractmethod
    def map_requests(self, func: Callable[[Request], Any], requests: Optional[List[Request]] = None) -> List[Any]:
        """Apply a function to each request and return the list of results."""
        pass

    @abstractmethod
    def count_by_method(self, requests: Optional[List[Request]] = None) -> Dict[str, int]:
        """Count requests by HTTP method."""
        pass

    @abstractmethod
    def count_by_status_code(self, requests: Optional[List[Request]] = None) -> Dict[int, int]:
        """Count requests by response status code."""
        pass