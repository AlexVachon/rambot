import time
from typing import List, Optional

from botasaurus_driver.driver import Driver as BTDriver, cdp
from botasaurus_driver.core import util, element
from .element import Element, make_element


class Driver(BTDriver):
    """
    Enhanced Botasaurus Driver with XPath search support,
    both global and scoped to a root Element.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the Driver.

        Args:
            **kwargs: Any arguments to pass to the base BTDriver.
        """
        super().__init__(**kwargs)

    def find_by_xpath(
        self,
        query: str,
        root: Optional[Element] = None,
        timeout: int = 10
    ) -> List[Element]:
        """
        Find elements matching an XPath query.

        Can search globally (document-wide) or scoped to a given root Element.

        Args:
            query: XPath query string.
            root: Optional root Element to scope the search.
            timeout: Maximum time to retry in seconds.

        Returns:
            List of Element instances matching the XPath.
        """
        self._enable_agents()

        if root is not None and not query.startswith("."):
            query = "." + query

        start_time: float = time.time()
        while True:
            try:
                doc = self._get_full_document()
                if root is not None:
                    results: List[Element] = self._find_scoped(doc, root, query)
                else:
                    results = self._find_global(doc, query)

                if results:
                    return results

            except Exception:
                pass

            if time.time() - start_time >= timeout:
                break

            time.sleep(0.2)

        return []

    # -------------------------------
    # Helper methods
    # -------------------------------

    def _enable_agents(self) -> None:
        """
        Enable the DOM and Runtime agents in the browser tab.
        """
        self._tab.send(cdp.dom.enable())
        self._tab.send(cdp.runtime.enable())

    def _get_full_document(self) -> "cdp.dom.Node":
        """
        Fetch the full DOM document, including shadow DOMs.

        Returns:
            The root DOM Node of the document.
        """
        return self._tab.send(cdp.dom.get_document(depth=-1, pierce=True))

    def _find_scoped(self, doc: "cdp.dom.Node", root: Element, query: str) -> List[Element]:
        """
        Perform an XPath search scoped to a given root Element.

        Args:
            doc: Full document root Node.
            root: Element to scope the XPath search.
            query: XPath query string (should start with `.` for relative search).

        Returns:
            List of Elements matching the XPath relative to the root.
        """
        results: List[Element] = []

        backend_node_id: int = root._elem._node.backend_node_id
        remote_root: "cdp.runtime.RemoteObject" = self._tab.send(
            cdp.dom.resolve_node(backend_node_id=backend_node_id)
        )

        js: str = """
        function(xpath) {
            const out = [];
            const iter = document.evaluate(
                xpath,
                this,
                null,
                XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                null
            );
            for (let i = 0; i < iter.snapshotLength; i++) {
                out.push(iter.snapshotItem(i));
            }
            return out;
        }
        """

        result: "cdp.runtime.RemoteObject"
        exception: Optional[dict]
        result, exception = self._tab.send(
            cdp.runtime.call_function_on(
                function_declaration=js,
                object_id=remote_root.object_id,
                arguments=[cdp.runtime.CallArgument(value=query)],
                return_by_value=False,
            )
        )

        if exception:
            raise RuntimeError(exception)

        array_obj_id: str = result.object_id

        # Fetch array properties representing the elements
        props, _, exception, _ = self._tab.send(
            cdp.runtime.get_properties(object_id=array_obj_id, own_properties=True)
        )
        if exception:
            raise RuntimeError(exception)

        for prop in props:
            if not hasattr(prop, "name") or not prop.name.isdigit():
                continue
            if not prop.value or not getattr(prop.value, "object_id", None):
                continue

            node_id: int = self._tab.send(
                cdp.dom.request_node(object_id=prop.value.object_id)
            )

            node: Optional["cdp.dom.Node"] = util.filter_recurse(
                doc, lambda n: n.node_id == node_id
            )

            if node:
                internal = element.create(node, self._tab, doc)
                results.append(make_element(self, self._tab, internal))

        return results

    def _find_global(self, doc: "cdp.dom.Node", query: str) -> List[Element]:
        """
        Perform a document-wide XPath search.

        Args:
            doc: Full document root Node.
            query: XPath query string.

        Returns:
            List of Elements matching the XPath in the entire document.
        """
        results: List[Element] = []

        search_id: str
        count: int
        search_id, count = self._tab.send(cdp.dom.perform_search(query=query))

        if count:
            node_ids: List[int] = self._tab.send(
                cdp.dom.get_search_results(search_id=search_id, from_index=0, to_index=count)
            )
            for node_id in node_ids:
                node: Optional["cdp.dom.Node"] = util.filter_recurse(
                    doc, lambda n: n.node_id == node_id
                )
                if node:
                    internal = element.create(node, self._tab, doc)
                    results.append(make_element(self, self._tab, internal))

            self._tab.send(cdp.dom.discard_search_results(search_id=search_id))

        return results
