from __future__ import annotations

import logging
import typing as t

from starlette.exceptions import HTTPException

from fastapi_problem.handler.base import ExceptionHandler, cors_wrapper_factory, http_exception_handler

if t.TYPE_CHECKING:
    from starlette.applications import Starlette

    from fastapi_problem.cors import CorsConfiguration
    from fastapi_problem.error import StatusProblem

logger_ = logging.getLogger(__name__)


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
        },
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
    )
    return cors_wrapper_factory(cors, handler) if cors else handler


def add_exception_handler(  # noqa: PLR0913
    app: Starlette,
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
