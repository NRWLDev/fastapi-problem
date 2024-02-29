from __future__ import annotations

import json
import logging
import typing

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from web_error import constant
from web_error.error import HttpCodeException, HttpException
from web_error.handler.starlette import cors_wrapper_factory

if typing.TYPE_CHECKING:
    from starlette.requests import Request

    from web_error.cors import CorsConfiguration

logger_ = logging.getLogger(__name__)


def exception_handler_factory(
    logger: logging.Logger,
    unhandled_wrappers: dict[str, type[HttpCodeException]],
    *,
    strip_debug: bool = False,
) -> typing.Callable[[Exception], JSONResponse]:
    unhandled_wrappers = unhandled_wrappers or {}

    def exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        wrapper = unhandled_wrappers.get("default", unhandled_wrappers.get("500"))
        ret = wrapper(str(exc)) if wrapper else HttpException("Unhandled exception occurred.", str(exc))
        headers = {}

        if isinstance(exc, HTTPException):
            wrapper = unhandled_wrappers.get(str(exc.status_code))
            debug_message = exc.detail
            ret = (
                wrapper(debug_message)
                if wrapper
                else HttpException("Unhandled HTTPException occurred.", debug_message, status=exc.status_code)
            )
            headers = exc.headers

        if isinstance(exc, RequestValidationError):
            wrapper = unhandled_wrappers.get("422")
            debug_message = json.loads(json.dumps(exc.errors(), default=str))
            ret = (
                wrapper(debug_message)
                if wrapper
                else HttpException("Request validation error.", debug_message, status=422)
            )

        if isinstance(exc, HttpException):
            ret = exc

        if ret.status >= constant.SERVER_ERROR:
            logger.exception(ret.message, exc_info=(type(exc), exc, exc.__traceback__))

        if strip_debug and ret.debug_message:
            msg = f"Removed debug message: {ret.debug_message}"
            logger.debug(msg)

        return JSONResponse(
            status_code=ret.status,
            content=ret.marshal(strip_debug=strip_debug),
            headers=headers,
        )

    return exception_handler


def generate_handler(
    logger: logging.Logger = logger_,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[HttpCodeException]] | None = None,
    *,
    strip_debug: bool = False,
) -> typing.Callable:
    handler = exception_handler_factory(
        logger=logger,
        unhandled_wrappers=unhandled_wrappers,
        strip_debug=strip_debug,
    )
    return cors_wrapper_factory(cors, handler) if cors else handler
