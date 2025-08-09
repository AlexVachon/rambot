import os
import json
import tempfile

from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Dict, Any, Tuple

from .scraper import IScraper
from .request import Response, Request


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
    def requests(
        self,
        predicate: Optional[Callable[[Request], bool]] = None
    ) -> List[Request]:
        """
        Retrieve all captured requests, optionally filtered by a predicate.

        Args:
            predicate (Optional[Callable[[Request], bool]]): 
                A function that takes a Request object and returns True if the request
                should be included in the result. If None, all requests are returned.

        Returns:
            List[Request]: List of captured Request objects that satisfy the predicate.
        """
        pass
    
    def _requests(self) -> List[Request]:
        """
        Read and parse the raw captured requests from the storage file.

        Reads the requests from the internal JSON file at self._requests_path,
        parses each line into a Request object including its associated Response.

        Returns:
            List[Request]: All captured requests parsed from the storage file.
                        Returns an empty list if the file does not exist or is empty.
        """
        if not os.path.exists(self._requests_path):
            return []

        requests_list = []
        with open(self._requests_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)

                    req_data = data["request"]
                    res_data = data["response"]

                    response_obj = Response(
                        url=res_data.get("url", req_data.get("url", "")),
                        status_code=res_data.get("status_code", 0),
                        headers=res_data.get("headers", {}),
                        body=res_data.get("body", "")
                    )

                    request_obj = Request(
                        method=req_data.get("method", ""),
                        url=req_data.get("url", ""),
                        headers=req_data.get("headers", {}),
                        body=req_data.get("body", ""),
                        response=response_obj
                    )

                    requests_list.append(request_obj)
                except json.JSONDecodeError as e:
                    pass
        return requests_list

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