import logging
from typing import Callable

from aiohttp import web, web_exceptions

from web_error import constant, error

logger = logging.getLogger(__name__)


def view_error_handler(view_method: Callable) -> Callable:
    async def wrapped_view_method(*args, **kwargs) -> web.Response:
        message = "Unhandled exception occurred."
        status = constant.SERVER_ERROR
        try:
            return await view_method(*args, **kwargs)
        except error.HttpException as ex:
            message = ex.message
            status = ex.status
            response = web.json_response(data=ex.marshal(), status=ex.status)
        except web_exceptions.HTTPError as ex:
            message = "Http error occurred."
            response = web.json_response(
                data={"message": ex.__class__.__name__, "debug_message": ex.text, "code": None},
                status=ex.status_code,
            )
        except Exception as e:  # noqa: BLE001
            response = web.json_response(
                data={"message": message, "debug_message": str(e), "code": None},
                status=status,
            )
        if status >= constant.SERVER_ERROR:
            logger.exception(message)
        return response

    return wrapped_view_method
