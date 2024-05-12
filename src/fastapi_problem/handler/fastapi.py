from __future__ import annotations

import json
import logging
import typing as t

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from fastapi_problem.error import Problem, StatusProblem
from fastapi_problem.handler.base import ExceptionHandler, cors_wrapper_factory, http_exception_handler

if t.TYPE_CHECKING:
    from fastapi import FastAPI
    from starlette.requests import Request

    from fastapi_problem.cors import CorsConfiguration

logger_ = logging.getLogger(__name__)


def request_validation_handler(
    eh: ExceptionHandler,
    _request: Request,
    exc: RequestValidationError,
) -> tuple[dict, Problem]:
    wrapper = eh.unhandled_wrappers.get("422")
    errors = json.loads(json.dumps(exc.errors(), default=str))
    kwargs = {"errors": errors}
    ret = (
        wrapper(**kwargs)
        if wrapper
        else Problem(
            title="Request validation error.",
            code="request-validation-failed",
            status=422,
            **kwargs,
        )
    )

    return {}, ret


def generate_handler(
    logger: logging.Logger = logger_,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    *,
    strip_debug: bool = False,
    strip_debug_codes: list[int] | None = None,
) -> t.Callable:
    handler = ExceptionHandler(
        logger=logger,
        unhandled_wrappers=unhandled_wrappers,
        handlers={
            HTTPException: http_exception_handler,
            RequestValidationError: request_validation_handler,
        },
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
    )
    return cors_wrapper_factory(cors, handler) if cors else handler


def add_exception_handler(  # noqa: PLR0913
    app: FastAPI,
    logger: logging.Logger = logger_,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    *,
    strip_debug: bool = False,
    strip_debug_codes: list[int] | None = None,
) -> None:
    eh = generate_handler(
        logger,
        cors,
        unhandled_wrappers,
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
    )
    app.exception_handler(Exception)(eh)
    app.exception_handler(HTTPException)(eh)
    app.exception_handler(RequestValidationError)(eh)
