import os
import json
import tempfile

from abc import ABC, abstractmethod
from typing import Optional, Callable, List

from .scraper import IScraper
from .request import Response, Request


class IInterceptor(ABC):
    """
    Abstract Base Class for a request interceptor used in web scraping.

    An interceptor acts as a proxy that sits between the scraper and the web,
    allowing the framework to inspect network calls (XHR, images, etc.) made
    by the browser.
    """

    _scraper: IScraper
    _requests_path: str

    def __init__(self, scraper: IScraper) -> None:
        """
        Initialize the interceptor.

        Args:
            scraper (IScraper): The parent scraper instance, used to access 
                logging and proxy configuration.
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
        Start the network interception process.
        
        This should initialize any background processes or proxies needed
        to capture traffic.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop interception and perform cleanup.
        
        This should terminate background processes and delete temporary files.
        """
        pass

    @abstractmethod
    def requests(
        self,
        predicate: Optional[Callable[[Request], bool]] = None
    ) -> List[Request]:
        """
        Retrieve captured requests.

        Args:
            predicate (Optional[Callable[[Request], bool]]): Filter function.

        Returns:
            List[Request]: List of captured network objects.
        """
        pass
    
    def _requests(self) -> List[Request]:
        """
        Internal helper to parse captured traffic from the local storage file.

        Reads the JSONL file line-by-line and reconstructs Request and Response 
        objects. This is designed to be memory efficient for large logs.

        Returns:
            List[Request]: Reconstructed request objects with nested responses.
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
                        status=res_data.get("status", 0),
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
                except json.JSONDecodeError:
                    pass
        return requests_list
