import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from web_error.error import HttpException


logger = logging.getLogger(__name__)


def exception_handler(request: Request, exc: Exception):
    status = 500
    message = "Unhandled exception occured."
    response = {
        "message": message,
        "debug_message": str(exc),
        "code": None,
    }

    if isinstance(exc, HttpException):
        response = exc.marshal()
        status = exc.status

    if status >= 500:
        logger.exception(message)

    return JSONResponse(
        status_code=status,
        content=response,
    )
