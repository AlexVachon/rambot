from typing import Generator, Optional, Dict, Any
from .util import CDP_DICT

def enable() -> Generator[CDP_DICT, CDP_DICT, None]:
    """Enables the runtime domain notifications."""
    resp = yield {"method": "Runtime.enable"}
    return resp

def evaluate(
    expression: str,
    *,
    context_id: Optional[int] = None,
    object_group: Optional[str] = None,
    include_command_line_api: Optional[bool] = None,
    silent: Optional[bool] = None,
    return_by_value: Optional[bool] = None,
    generate_preview: Optional[bool] = None,
    await_promise: Optional[bool] = None
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Evaluates JavaScript expressions in the context of the page."""
    params: CDP_DICT = {"expression": expression}
    if context_id:
        params["contextId"] = context_id
    if object_group:
        params["objectGroup"] = object_group
    if include_command_line_api is not None:
        params["includeCommandLineAPI"] = include_command_line_api
    if silent is not None:
        params["silent"] = silent
    if return_by_value is not None:
        params["returnByValue"] = return_by_value
    if generate_preview is not None:
        params["generatePreview"] = generate_preview
    if await_promise is not None:
        params["awaitPromise"] = await_promise

    resp = yield {
        "method": "Runtime.evaluate",
        "params": params
    }
    return resp

def call_function_on(
    object_id: str,
    function_name: str,
    *args: Dict[str, Any],
    **kwargs: Dict[str, Any]
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Calls a function on the specified object."""
    params: CDP_DICT = {
        "objectId": object_id,
        "functionName": function_name,
        "arguments": args,
        **kwargs
    }

    resp = yield {
        "method": "Runtime.callFunctionOn",
        "params": params
    }
    return resp

def get_properties(
    object_id: str,
    *,
    own_properties: Optional[bool] = True,
    accessor_properties_only: Optional[bool] = False
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Gets properties of the specified object."""
    params: CDP_DICT = {"objectId": object_id}
    if own_properties is not None:
        params["ownProperties"] = own_properties
    if accessor_properties_only is not None:
        params["accessorPropertiesOnly"] = accessor_properties_only

    resp = yield {
        "method": "Runtime.getProperties",
        "params": params
    }
    return resp

def release_object(
    object_id: str
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Releases the specified object."""
    resp = yield {
        "method": "Runtime.releaseObject",
        "params": {"objectId": object_id}
    }
    return resp

def release_object_group(
    object_group: str
) -> Generator[CDP_DICT, CDP_DICT, None]:
    """Releases all objects in the specified group."""
    resp = yield {
        "method": "Runtime.releaseObjectGroup",
        "params": {"objectGroup": object_group}
    }
    return resp