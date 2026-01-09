from typing import Generator, Optional, Dict, Any
from .util import CDP_DICT

def enable() -> Generator[CDP_DICT, CDP_DICT, None]:
    """Enables page domain notifications."""
    resp = yield {"method": "Page.enable"}
    return resp

def add_script_to_evaluate_on_new_document(
    source: str,
    *,
    world_name: Optional[str] = None,
    include_command_line_api: Optional[bool] = None,
    run_immediately: Optional[bool] = None
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Adds a script to evaluate on new documents."""
    params: CDP_DICT = {"source": source}
    if world_name:
        params["worldName"] = world_name
    if include_command_line_api is not None:
        params["includeCommandLineAPI"] = include_command_line_api
    if run_immediately is not None:
        params["runImmediately"] = run_immediately

    resp = yield {
        "method": "Page.addScriptToEvaluateOnNewDocument",
        "params": params
    }
    return resp

def navigate(
    url: str,
    *,
    referrer: Optional[str] = None,
    frame_id: Optional[str] = None,
    transition_type: Optional[str] = None,
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Navigates the page to the specified URL."""
    params: CDP_DICT = {"url": url}
    if referrer:
        params["referrer"] = referrer
    if frame_id:
        params["frameId"] = frame_id
    if transition_type:
        params["transitionType"] = transition_type

    resp = yield {
        "method": "Page.navigate",
        "params": params
    }
    return resp

def get_navigation_history(
    *,
    session_id: Optional[str] = None
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Retrieves the navigation history for a specific page/session."""
    message: CDP_DICT = {
        "method": "Page.getNavigationHistory"
    }
    if session_id:
        message["sessionId"] = session_id

    resp = yield message
    return resp

def stop_loading() -> Generator[CDP_DICT, CDP_DICT, None]:
    """Stops the page's loading process."""
    resp = yield {"method": "Page.stopLoading"}
    return resp

def reload(
    *,
    ignore_cache: Optional[bool] = False,
    script_to_evaluate_on_load: Optional[str] = None
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Reloads the page."""
    params: CDP_DICT = {"ignoreCache": ignore_cache}
    if script_to_evaluate_on_load:
        params["scriptToEvaluateOnLoad"] = script_to_evaluate_on_load

    resp = yield {
        "method": "Page.reload",
        "params": params
    }
    return resp

def set_document_content(
    html: str
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Sets the document content."""
    resp = yield {
        "method": "Page.setDocumentContent",
        "params": {"html": html}
    }
    return resp

def capture_screenshot(
    *,
    format_: Optional[str] = "png",
    quality: Optional[int] = None,
    clip: Optional[Dict[str, Any]] = None,
    from_surface: Optional[bool] = False
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Captures a screenshot of the page."""
    params: CDP_DICT = {"format": format_, "fromSurface": from_surface}
    if quality:
        params["quality"] = quality
    if clip:
        params["clip"] = clip

    resp = yield {
        "method": "Page.captureScreenshot",
        "params": params
    }
    return resp

def bring_to_front() -> Generator[CDP_DICT, CDP_DICT, None]:
    """Brings the page to the front."""
    resp = yield {"method": "Page.bringToFront"}
    return resp

def close() -> Generator[CDP_DICT, CDP_DICT, None]:
    """Closes the page."""
    resp = yield {"method": "Page.close"}
    return resp

def load_event_fired() -> Generator[CDP_DICT, CDP_DICT, None]:
    return (yield {
        "method": "Page.loadEventFired",
        "params": {
            "timestamp": 12345.67
        }
    })