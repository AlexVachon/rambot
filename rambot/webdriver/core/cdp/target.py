import json
from typing import Generator, Dict, Any

CDP_DICT = Dict[str, Any]


def enable() -> Generator[CDP_DICT, CDP_DICT, None]:
    return (yield {
        "method": "Target.setDiscoverTargets",
        "params": {"discover": True}
    })

def get_targets() -> Generator[CDP_DICT, CDP_DICT, None]:
    cmd = yield {
        "method": "Target.getTargets"
    }
    return cmd

def create_target(url: str = "about:blank") -> Generator[CDP_DICT, CDP_DICT, None]:
    cmd = yield {"method": "Target.createTarget", "params": {"url": url}}
    return cmd

def close_target(target_id: str) -> Generator[CDP_DICT, CDP_DICT, None]:
    cmd = yield {"method": "Target.closeTarget", "params": {"targetId": target_id}}
    return cmd

def activate_target(target_id: str) -> Generator[CDP_DICT, CDP_DICT, None]:
    cmd = yield {"method": "Target.activateTarget", "params": {"targetId": target_id}}
    return cmd

def send_message_to_target(target_id: str, method: str, params: Dict = {}) -> Generator[CDP_DICT, CDP_DICT, None]:
    cmd = yield {
        "method": "Target.sendMessageToTarget",
        "params": {
            "targetId": target_id,
            "message": json.dumps({
                "id": 1,
                "method": method,
                "params": params
            })
        }
    }
    return cmd

def attach_to_target(target_id, flatten=True) -> Generator[CDP_DICT, CDP_DICT, None]:
    return (yield {
        "method": "Target.attachToTarget",
        "params": {
            "targetId": target_id,
            "flatten": flatten
        }
    })

def detach_from_target(session_id) -> Generator[CDP_DICT, CDP_DICT, None]:
    return (yield {
        "method": "Target.detachFromTarget",
        "params": {
            "sessionId": session_id
        }
    })


def get_target_info(target_id: str) -> Generator[CDP_DICT, CDP_DICT, None]:
    return (yield {
        "method": "Target.getTargetInfo",
        "params": {
            "targetId": target_id
        }
    })