from typing import List, Optional

from botasaurus_driver.driver import Wait

from ..types import IHTML
from ..browser.driver import Driver
from ..browser.element import Element
from ..helpers import By


class HTML(IHTML):
    """
    A high-level wrapper for browser DOM interactions and element searching.

    This class provides a unified interface for finding and interacting with web elements
    using both CSS Selectors and XPath queries. It leverages the underlying Driver
    to handle complex CDP-based searches and polling.
    """

    def __init__(self, driver: Driver):
        """
        Initializes the HTML wrapper with a driver instance.

        Args:
            driver (Driver): The custom Rambot Driver instance used for DOM operations.
        """
        self._driver = driver

    @property
    def driver(self) -> Driver:
        """
        Returns the underlying Driver instance.

        Returns:
            Driver: The active browser driver or None if not initialized.
        """
        return getattr(self, "_driver", None)

    def _execute_search(self, query: str, by: By, root: Optional[Element], timeout: int) -> List[Element]:
        """
        Internal dispatcher to execute element searches based on locator type.

        Args:
            query (str): The search query (CSS selector or XPath string).
            by (By): The locator strategy to use (SELECTOR or XPATH).
            root (Optional[Element]): The element to search within. If None, searches the document.
            timeout (int): Maximum time in seconds to wait for elements to appear.

        Returns:
            List[Element]: A list of wrapped elements found.

        Raises:
            ValueError: If an unsupported locator type is provided.
        """
        if by == By.SELECTOR:
            return root.select_all(query, wait=timeout) if root else self.driver.select_all(query, wait=timeout)
        elif by == By.XPATH:
            return self.driver.find_by_xpath(query=query, root=root, timeout=timeout)
        
        raise ValueError(f"Unsupported locator type: {by}")

    def find(self, query: str, by: By = By.XPATH, root: Optional[Element] = None, timeout: int = 10) -> Element:
        """
        Locates the first matching element within the specified timeout.

        This method should be used when you expect a single element to be present
        and want to interact with it (e.g., clicking a button or reading a text label).

        Args:
            query (str): The search query string.
            by (By): The strategy to locate the element (defaults to By.XPATH).
            root (Optional[Element]): An optional element to use as the search scope.
            timeout (int): Seconds to poll for the element's existence. Defaults to 10.

        Returns:
            Element: The first wrapped element found.

        Raises:
            Exception: If no matching element is found within the given timeout period.
        """
        elements = self._execute_search(query, by, root, timeout)
        if not elements:
            return None
        return elements[0]

    def find_all(self, query: str, by: By = By.XPATH, root: Optional[Element] = None, timeout: int = 10) -> List[Element]:
        """
        Locates all matching elements within the specified timeout.

        This method is ideal for finding lists of items, such as search results,
        table rows, or menu items.

        Args:
            query (str): The search query string.
            by (By): The strategy to locate elements (defaults to By.XPATH).
            root (Optional[Element]): An optional element to use as the search scope.
            timeout (int): Seconds to poll for at least one element to appear. Defaults to 10.

        Returns:
            List[Element]: A list of all matching wrapped elements. Returns an empty 
                list if no matches are found after the timeout.
        """
        return self._execute_search(query, by, root, timeout)

    def click(self, query: str, by: By = By.XPATH, timeout: int = Wait.SHORT) -> bool:
        """
        Attempts to find and click an element.

        This is a high-level convenience method that handles error catching.
        It is particularly useful for clicking optional elements or dismissable popups.

        Args:
            query (str): The search query string.
            by (By): The strategy to locate the element (defaults to By.XPATH).
            timeout (int): Maximum time to wait for the element. Defaults to Wait.SHORT.

        Returns:
            bool: True if the element was successfully found and clicked; False otherwise.
        """
        try:
            element = self.find(query, by=by, timeout=timeout)
            self.driver.click(element, wait=timeout)
            return True
        except Exception:
            return False
        
    def is_element_visible(self, query: str, by: By = By.XPATH, timeout: int = Wait.SHORT) -> bool:
        """
        Implementation that safely checks visibility without raising exceptions.
        """
        try:
            elements = self._execute_search(query, by, None, timeout)
            
            if elements:
                return elements[0].is_visible()
            
            return False
        except Exception:
            return False