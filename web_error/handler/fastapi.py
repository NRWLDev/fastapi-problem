import json
import logging

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from web_error.error import HttpException
from web_error.handler import starlette


logger = logging.getLogger(__name__)


def exception_handler(request: starlette.Request, exc: Exception):
    status = 500
    message = "Unhandled exception occurred."
    response = {
        "message": message,
        "debug_message": str(exc),
        "code": None,
    }

    if isinstance(exc, HTTPException):
        response["message"] = exc.detail
        status = exc.status_code

    if isinstance(exc, RequestValidationError):
        response["message"] = "Request validation error."
        response["debug_message"] = json.loads(exc.json())
        status = 422

    if isinstance(exc, HttpException):
        response = exc.marshal()
        status = exc.status

    if status >= 500:
        logger.exception(message, exc_info=(type(exc), exc, exc.__traceback__))

    return starlette.JSONResponse(
        status_code=status,
        content=response,
    )


def generate_handler_with_cors(
    allow_origins=None,
    allow_credentials=True,
    allow_methods=None,
    allow_headers=None,
):
    return starlette.generate_handler_with_cors(
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        _exception_handler=exception_handler,
    )
