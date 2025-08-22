from typing import Generator, Optional, Dict, Any
from .util import CDP_DICT

def enable(
    *,
    max_total_buffer_size: Optional[int] = None,
    max_resource_buffer_size: Optional[int] = None,
    max_post_data_size: Optional[int] = None
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Enables the network domain notifications."""
    params: CDP_DICT = {}
    if max_total_buffer_size is not None:
        params["maxTotalBufferSize"] = max_total_buffer_size
    if max_resource_buffer_size is not None:
        params["maxResourceBufferSize"] = max_resource_buffer_size
    if max_post_data_size is not None:
        params["maxPostDataSize"] = max_post_data_size

    resp = yield {
        "method": "Network.enable",
        "params": params
    }
    return resp

def set_user_agent_override(
    user_agent: str,
    *,
    accept_language: Optional[str] = None,
    platform: Optional[str] = None
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Overrides the default user agent."""
    params: CDP_DICT = {"userAgent": user_agent}
    if accept_language:
        params["acceptLanguage"] = accept_language
    if platform:
        params["platform"] = platform

    resp = yield {
        "method": "Network.setUserAgentOverride",
        "params": params
    }
    return resp

def set_request_interception(
    patterns: list[Dict[str, Any]]
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Sets the request interception patterns."""
    resp = yield {
        "method": "Network.setRequestInterception",
        "params": {"patterns": patterns}
    }
    return resp

def get_response_body(
    request_id: str
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Gets the response body for a given request."""
    resp = yield {
        "method": "Network.getResponseBody",
        "params": {"requestId": request_id}
    }
    return resp

def replay_xhr(
    request_id: str
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Replays an XHR request."""
    resp = yield {
        "method": "Network.replayXHR",
        "params": {"requestId": request_id}
    }
    return resp