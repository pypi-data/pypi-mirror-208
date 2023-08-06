import json
from asyncio.futures import Future
from typing import Any, Set

from starlette.responses import JSONResponse

from exodusutils.exceptions import ExodusError


class CustomJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return json.dumps(content, allow_nan=True).encode("utf-8")


def handle_future(completed_tasks: Set[Future]):
    """
    Handles a single future. If it failed, return the exception, otherwise return the result.
    """
    if len(completed_tasks) != 1:
        return ExodusError(
            f"Finished {len(completed_tasks)} even though there is only one task to be done"
        )
    for task in completed_tasks:
        if task.exception() is not None:
            return task.exception()
        else:
            return task.result()


def consume_result(res):
    """
    Consumes the result from the task finished in the event loop. If there's an error, raise it.
    """
    if isinstance(res, Exception) or isinstance(res, BaseException):
        raise res
    elif res is None:
        raise ExodusError("Failed to run simple request, something is wrong")
    else:
        return res
