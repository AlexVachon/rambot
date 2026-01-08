from typing import List, Union

from botasaurus_driver.driver import Wait

from ..types import IHTML
from ..browser.driver import Driver
from ..browser.element import Element

from ..helpers import By


class HTML(IHTML):
    def __init__(self, driver: Driver):
        self._driver = driver

    @property
    def driver(self) -> Driver:
        if hasattr(self, "_driver"):
            return self._driver
        return None
    
    def find(
        self, 
        query, 
        *, 
        by = By.XPATH, 
        root = None, 
        first: bool = False, 
        timeout = 10
    )  -> Element | List[Element]:
        elements = []

        if by == By.SELECTOR:
            elements = root.select_all(query, wait=timeout) if root else self.driver.select_all(query, wait=timeout)
        elif by == By.XPATH:
            elements = self.driver.find_by_xpath(query=query, root=root, timeout=timeout)
        else:
            raise ValueError(f"Unsupported locator type: {by}")

        if first:
            if not elements:
                raise Exception("No element found")
            return elements[0]
        
        return elements
    
    def click(self, query, by = By.XPATH, timeout = Wait.SHORT) -> bool:
        try:
            element = self.find(query, by=by, first=True, timeout=timeout)
            if not element:
                return False
            self.driver.click(element, wait=timeout)
            return True
        except Exception as e:
            return False

    def is_element_visible(self, selector, wait=Wait.SHORT): return self.driver.is_element_present(selector, wait)
