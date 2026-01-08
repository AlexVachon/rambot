from typing import Optional, List, Any

from botasaurus_driver.driver import Wait
from botasaurus_driver.driver import Element as BTElement, create_iframe_element


class Element(BTElement):
    
    def __init__(self, driver, tab, internal_element, elem=None):
        super().__init__(driver, tab, internal_element, elem or internal_element)
        
    def get(self, key: str, default: Any = None) -> Any:
        try:
            value = self.attrs.get(key, default)
            return value
        except Exception:
            return default
        
    @property
    def attrs(self):
        return self.attributes

    @property
    def inner_html(self) -> str:
        return self.run_js("(el) => el.innerHTML")

    @property
    def outer_html(self) -> str:
        return self.run_js("(el) => el.outerHTML")

    @property
    def is_visible(self) -> bool:
        return self.run_js("(el) => {"
                           "const style = window.getComputedStyle(el);"
                           "return !(style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0);"
                           "}")
    
    def select_all(
        self, selector: str, wait: Optional[int] = Wait.SHORT
    ) -> List["Element"]:
        elems_coro = self._elem.query_selector_all(selector, wait)
        elems = self._tab._run(elems_coro)
        
        return [make_element(self.driver, self.tab, e) for e in elems]
    

def make_element(driver, tab, internal_element):
    if not internal_element:
        return None
    if internal_element._node.node_name == "IFRAME":
        return create_iframe_element(driver, internal_element)
    else:
        return Element(driver, tab, internal_element)