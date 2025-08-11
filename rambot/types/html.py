from abc import ABC, abstractmethod
from typing import Union, List, Optional

from botasaurus_driver.driver import Wait

from ..browser.driver import Driver
from ..browser.element import Element
from ..helpers import By


class IHTML(ABC):
    _driver: Driver

    @property
    @abstractmethod
    def driver() -> Driver:
        """Returns the driver instance."""
        pass

    @abstractmethod
    def find(self, query: str, *, by: By = By.XPATH, root: Optional[Element] = None, first: bool = False, timeout: int = 10) -> Union[Element, List[Element]]:
        """
        Finds elements based on the query and returns either a single element or a list of elements.
        
        :param query: The query to find elements.
        :param by: The method to use for finding elements (default is By.XPATH).
        :param root: The root element to search within (optional).
        :param first: If True, returns only the first found element.
        :param timeout: The maximum time to wait for elements to be found.
        :return: A single Element or a list of Elements.
        """
        pass

    @abstractmethod
    def click(self, query, by = By.XPATH, timeout = Wait.SHORT) -> bool:
        """
        Clicks on an element found by the query.
        
        :param query: The query to find the element to click.
        :param by: The method to use for finding the element (default is By.XPATH).
        :param timeout: The maximum time to wait for the element to be clickable.
        :return: True if the click was successful, False otherwise.
        """
        pass

    @abstractmethod
    def is_element_visible(self, selector, wait=Wait.SHORT) -> bool:
        """
        Checks if an element is visible.
        
        :param selector: The selector to find the element.
        :param wait: The maximum time to wait for the element to be visible.
        :return: True if the element is visible, False otherwise.
        """
        pass