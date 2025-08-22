from .core import cdp, util
from .core.base import DriverBase

from .tab import Tab


class Driver(DriverBase):
    def __init__(self, chromedriver_path="chromedriver", headless=False, port=9515):
        super().__init__(chromedriver_path, headless, port)

        targets = self._run_cdp_command(cdp.target.get_targets())
        self._tabs = [Tab(self, t) for t in targets.get("targetInfos", []) if t.get("type") == "page"]

        if not self._tabs:
            raise RuntimeError("No page target found at startup.")

        self._tab = self._tabs[0]

    @property
    def tab(self) -> "Tab":
        """Onglet actif (lecture/écriture)."""
        return self._tab

    @tab.setter
    def tab(self, tab: "Tab"):
        if tab not in self.tabs:
            raise ValueError("Tab must belong to this driver")
        self.switch_to_tab(tab)

    @property
    def tabs(self):
        return list(self._tabs)

    # --- Gestion des onglets ---
    def new_tab(self, url: str):
        resp = self._run_cdp_command(cdp.target.create_target(url))
        target_id = resp["targetId"]

        target_info = self._run_cdp_command(
            cdp.target.get_target_info(target_id)
        )["targetInfo"]
        new_tab = Tab(self, target_info)

        self._tabs.append(new_tab)
        self.switch_to_tab(new_tab)
        return new_tab

    def close_tab(self, tab: Tab = None):
        tab = tab or self.tab
        self._run_cdp_command(cdp.target.close_target(tab.target_id))
        self._tabs = [t for t in self._tabs if t.target_id != tab.target_id]
        if self._tab == tab:
            self._tab = self._tabs[0] if self._tabs else None

    def switch_to_tab(self, tab: Tab):
        if tab not in self._tabs:
            raise ValueError("Tab must belong to this driver")
        tab.activate()

    # --- Propriétés pratiques ---
    @property
    def url(self):
        if not self.tab:
            return None
        result = self._run_cdp_command(
            cdp.runtime.evaluate("window.location.href", await_promise=True),
            session_id=self.tab._session_id
        )
        return result.get("result", {}).get("value")
    

    # --- methodes ---

    def get(self, url: str) -> Tab:
        if not self.tab:
            raise RuntimeError("No tab associated to driver.")
        return self.tab.get(url)