import json
import logging
from typing import List, Optional, Tuple

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from web_error import constant
from web_error.error import HttpException
from web_error.handler import starlette

logger = logging.getLogger(__name__)


def _handle_exception(exc: Exception) -> Tuple[dict, str]:
    status = constant.SERVER_ERROR
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

    if status >= constant.SERVER_ERROR:
        logger.exception(message, exc_info=(type(exc), exc, exc.__traceback__))

    return response, status


class ExceptionHandler:
    def __init__(self, unhandled_code: str, request_validation_code: str) -> None:
        self.unhandled_code = unhandled_code
        self.request_validation_code = request_validation_code

    def __call__(self, request: starlette.Request, exc: Exception) -> starlette.JSONResponse:  # noqa: ARG002
        response, status = _handle_exception(exc)

        if response["code"] is None:
            response["code"] = self.request_validation_code if status == 422 else self.unhandled_code  # noqa: PLR2004

        return starlette.JSONResponse(
            status_code=status,
            content=response,
        )


def exception_handler(request: starlette.Request, exc: Exception) -> starlette.JSONResponse:  # noqa: ARG001
    response, status = _handle_exception(exc)

    return starlette.JSONResponse(
        status_code=status,
        content=response,
    )


def generate_handler_with_cors(
    allow_origins: Optional[List[str]] = None,
    allow_credentials: bool = True,
    allow_methods: Optional[List[str]] = None,
    allow_headers: Optional[List[str]] = None,
) -> starlette.JSONResponse:
    return starlette.generate_handler_with_cors(
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        _exception_handler=exception_handler,
    )
