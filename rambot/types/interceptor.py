import os
import tempfile

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

from .scraper import IScraper


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
    def get_requests(self) -> List[dict]:
        """
        Retrieve all captured requests.

        Returns:
            list of dict: Parsed request data.
        """
        pass