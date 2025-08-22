from .core import cdp
from .core.base import TabBase

class Tab(TabBase):

    def refresh_info(self):
        """Met à jour les infos de cet onglet depuis CDP sans réinitialiser."""
        targets = self.driver._run_cdp_command(cdp.target.get_targets())
        for t in targets.get("targetInfos", []):
            if t.get("targetId") == self.target_id:
                self.type = t.get("type")
                self.title = t.get("title")
                self.url = t.get("url")
                self.attached = t.get("attached", False)
                self.browser_context_id = t.get("browserContextId")
                self.can_access_opener = t.get("canAccessOpener", None)
                break

    def activate(self) -> "Tab":
        """Active cet onglet dans Chrome et attache la session si nécessaire."""
        self.driver._run_cdp_command(cdp.target.activate_target(self.target_id))
        if not self._session_id:
            attach_res = self.driver._run_cdp_command(
                cdp.target.attach_to_target(self.target_id, flatten=True)
            )
            self._session_id = attach_res["sessionId"]
        self.driver._active_tab = self

    def get(self, url: str) -> "Tab":
        """Navigue vers une URL dans cet onglet."""
        if not self._session_id:
            raise RuntimeError("Tab must be attached before navigation")
        
        self.activate()
        self.driver._run_cdp_command(
            cdp.page.navigate(url),
            session_id=self._session_id
        )
        self.driver._run_cdp_command(
            cdp.page.load_event_fired(),
            session_id=self._session_id
        )
        return self

    def evaluate(self, js: str, await_promise: bool = True):
        """Exécute du JS dans cet onglet."""
        self.activate()
        result = self.driver._run_cdp_command(
            cdp.runtime.evaluate(js, await_promise=await_promise),
            session_id=self._session_id
        )
        return result.get("result", {}).get("value")


