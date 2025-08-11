import time

from typing import List, Optional

from botasaurus_driver.driver import Driver as BTDriver, cdp
from botasaurus_driver.core import util, element
from .element import Element, make_element


class Driver(BTDriver):

    def find_by_xpath(
        self,
        query: str,
        root: Optional[Element] = None,
        timeout: int = 10
    ) -> List[Element]:
        results = []
        start_time = time.time()
        poll_interval = 0.1
        
        while True:
            results.clear()

            if root is not None:
                doc = root._elem._node
            else:
                doc = self._tab.send(cdp.dom.get_document(depth=-1, pierce=True))

            search_id, result_count = self._tab.send(
                cdp.dom.perform_search(query=query)
            )

            if result_count > 0:
                node_ids = self._tab.send(
                    cdp.dom.get_search_results(
                        search_id=search_id,
                        from_index=0,
                        to_index=result_count
                    )
                )
    
                for node_id in node_ids:
                    node = util.filter_recurse(doc, lambda n: n.node_id == node_id)
                    if not node:
                        continue
                    internal_element = element.create(node, self._tab, doc)
                    elem = make_element(self, self._tab, internal_element)
                    results.append(elem)

                if results:
                    return results

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                break

            time.sleep(poll_interval)   

        return results