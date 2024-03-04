from __future__ import annotations

import http
import json
import logging
import typing
from warnings import warn

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from web_error.error import HttpCodeException, HttpException
from web_error.handler.starlette import cors_wrapper_factory
from web_error.handler.util import convert_status_code

if typing.TYPE_CHECKING:
    from fastapi import FastAPI
    from starlette.requests import Request

    from web_error.cors import CorsConfiguration

logger_ = logging.getLogger(__name__)


def exception_handler_factory(
    logger: logging.Logger,
    unhandled_wrappers: dict[str, type[HttpCodeException]],
    *,
    strip_debug: bool = False,
    legacy: bool = False,
) -> typing.Callable[[Exception], JSONResponse]:
    unhandled_wrappers = unhandled_wrappers or {}

    def exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        wrapper = unhandled_wrappers.get("default", unhandled_wrappers.get("500"))
        ret = (
            wrapper(str(exc))
            if wrapper
            else HttpException(
                title="Unhandled exception occurred.",
                details=str(exc),
                code="unhandled-exception",
            )
        )
        headers = {}

        if isinstance(exc, HTTPException):
            wrapper = unhandled_wrappers.get(str(exc.status_code))
            details = exc.detail
            title, code = convert_status_code(exc.status_code)
            ret = (
                wrapper(details)
                if wrapper
                else HttpException(
                    title=title,
                    code=code,
                    details=details,
                    status=exc.status_code,
                )
            )
            headers = exc.headers or headers

        if isinstance(exc, RequestValidationError):
            wrapper = unhandled_wrappers.get("422")
            errors = json.loads(json.dumps(exc.errors(), default=str))
            kwargs = {"details": errors} if legacy else {"errors": errors}
            ret = (
                wrapper(**kwargs)
                if wrapper
                else HttpException(
                    title="Request validation error.",
                    code="request-validation-failed",
                    status=422,
                    **kwargs,
                )
            )

        if isinstance(exc, HttpException):
            ret = exc

        if ret.status >= http.HTTPStatus.INTERNAL_SERVER_ERROR:
            logger.exception(ret.title, exc_info=(type(exc), exc, exc.__traceback__))

        if strip_debug and (ret.details or ret.extras):
            msg = "Stripping debug information from exception."
            logger.debug(msg)

            for k, v in {
                "details": ret.details,
                **ret.extras,
            }.items():
                msg = f"Removed {k}: {v}"
                logger.debug(msg)

        if not legacy:
            headers["content-type"] = "application/problem+json"

        return JSONResponse(
            status_code=ret.status,
            content=ret.marshal(strip_debug=strip_debug, legacy=legacy),
            headers=headers,
        )

    return exception_handler


def generate_handler(
    logger: logging.Logger = logger_,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[HttpCodeException]] | None = None,
    *,
    strip_debug: bool = False,
    legacy: bool = False,
) -> typing.Callable:
    if legacy:
        warn(
            "legacy format is deprecated, please convert errors to RFC9547",
            DeprecationWarning,
            stacklevel=2,
        )
    handler = exception_handler_factory(
        logger=logger,
        unhandled_wrappers=unhandled_wrappers,
        strip_debug=strip_debug,
        legacy=legacy,
    )
    return cors_wrapper_factory(cors, handler) if cors else handler


def add_exception_handler(  # noqa: PLR0913
    app: FastAPI,
    logger: logging.Logger = logger_,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[HttpCodeException]] | None = None,
    *,
    strip_debug: bool = False,
    legacy: bool = False,
) -> None:
    eh = generate_handler(logger, cors, unhandled_wrappers, strip_debug=strip_debug, legacy=legacy)
    app.exception_handler(Exception)(eh)
    app.exception_handler(HTTPException)(eh)
    app.exception_handler(RequestValidationError)(eh)
