import logging

from aiohttp import web
from aiohttp import web_exceptions

from web_error import error


logger = logging.getLogger(__name__)


def view_error_handler(view_method):
    async def wrapped_view_method(*args, **kwargs):
        message = "Unhandled exception occured."
        status = 500
        try:
            return await view_method(*args, **kwargs)
        except error.HttpException as ex:
            message = ex.message
            status = ex.status
            response = web.json_response(data=ex.marshal(), status=ex.status)
        except web_exceptions.HTTPError as ex:
            message = "Http error occured."
            response = web.json_response(
                data={"message": ex.__class__.__name__, "debug_message": ex.text, "code": None},
                status=ex.status_code,
            )
        except Exception as e:
            response = web.json_response(
                data={"message": message, "debug_message": str(e), "code": None},
                status=status,
            )
        if status >= 500:
            logger.exception(message)
        return response

    return wrapped_view_method
