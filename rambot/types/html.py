from abc import ABC, abstractmethod
from typing import List, Optional

from botasaurus_driver.driver import Wait

from ..browser.driver import Driver
from ..browser.element import Element
from ..helpers import By


class IHTML(ABC):
    """
    Interface for HTML DOM interaction and element location strategies.

    This interface defines the contract for finding elements, checking visibility,
    and performing basic interactions like clicking. Implementations should provide
    robust polling and error handling.
    """
    _driver: Driver

    @property
    @abstractmethod
    def driver(self) -> Driver:
        """
        Provides access to the underlying browser driver instance.

        Returns:
            Driver: The active driver instance used for DOM operations.
        """
        pass

    @abstractmethod
    def find(
        self, 
        query: str, 
        by: By = By.XPATH, 
        root: Optional[Element] = None, 
        timeout: int = 10
    ) -> Element:
        """
        Locates the first matching element within the specified timeout.

        This method is intended for singular interactions where an element is 
        expected to exist.

        Args:
            query (str): The search query (CSS selector or XPath).
            by (By): The strategy used to locate the element. Defaults to By.XPATH.
            root (Optional[Element]): The scope within which to search. If None, 
                searches the entire document.
            timeout (int): Maximum seconds to wait for the element to appear.

        Returns:
            Element: The first matching wrapped element found.

        Raises:
            Exception: Implementations should raise an exception if no element 
                is found within the timeout.
        """
        pass

    @abstractmethod
    def find_all(
        self, 
        query: str, 
        by: By = By.XPATH, 
        root: Optional[Element] = None, 
        timeout: int = 10
    ) -> List[Element]:
        """
        Locates all matching elements within the specified timeout.

        This method is intended for retrieving lists of items. It should wait 
        until at least one element is found or the timeout is reached.

        Args:
            query (str): The search query (CSS selector or XPath).
            by (By): The strategy used to locate elements. Defaults to By.XPATH.
            root (Optional[Element]): The scope within which to search. If None, 
                searches the entire document.
            timeout (int): Maximum seconds to wait for elements to appear.

        Returns:
            List[Element]: A list of all matching wrapped elements found. 
                Should return an empty list if no matches are found after the timeout.
        """
        pass

    @abstractmethod
    def click(self, query: str, by: By = By.XPATH, timeout: int = Wait.SHORT) -> bool:
        """
        Attempts to locate and click an element found by the query.

        This method should encapsulate finding the element and performing the click 
        action, typically swallowing exceptions to return a success boolean.

        Args:
            query (str): The query to find the target element.
            by (By): The locator strategy. Defaults to By.XPATH.
            timeout (int): Seconds to wait for the element to be present and clickable.

        Returns:
            bool: True if the element was found and clicked successfully, False otherwise.
        """
        pass

    @abstractmethod
    def is_element_visible(
        self, 
        query: str, 
        by: By = By.XPATH, 
        timeout: int = Wait.SHORT
    ) -> bool:
        """
        Checks if an element is present in the DOM and visible within the viewport.

        Unlike find(), this method should not raise an exception if the element 
        is missing; it should instead return False.

        Args:
            query (str): The search query (CSS selector or XPath).
            by (By): The strategy used to locate the element. Defaults to By.XPATH.
            timeout (int): Maximum seconds to wait for the element to appear 
                and become visible. Defaults to Wait.SHORT.

        Returns:
            bool: True if the element is present and visible, False otherwise.
        """
        pass