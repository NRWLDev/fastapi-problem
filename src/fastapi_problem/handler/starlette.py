from __future__ import annotations

import logging
import typing as t

from starlette.exceptions import HTTPException

from fastapi_problem.handler.base import CorsPostHook, ExceptionHandler, http_exception_handler

if t.TYPE_CHECKING:
    from starlette.applications import Starlette

    from fastapi_problem.cors import CorsConfiguration
    from fastapi_problem.error import StatusProblem
    from fastapi_problem.handler.base import Handler, PostHook, PreHook

logger_ = logging.getLogger(__name__)


def generate_handler(  # noqa: PLR0913
    logger: logging.Logger = logger_,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    handlers: dict[Exception, Handler] | None = None,
    pre_hooks: list[PostHook] | None = None,
    post_hooks: list[PostHook] | None = None,
    *,
    strip_debug: bool = False,
    strip_debug_codes: list[int] | None = None,
) -> t.Callable:
    handlers = handlers or {}
    handlers.update({
        HTTPException: http_exception_handler,
    })
    pre_hooks = pre_hooks or []
    post_hooks = post_hooks or []

    if cors:
        post_hooks.append(CorsPostHook(cors))

    return ExceptionHandler(
        logger=logger,
        unhandled_wrappers=unhandled_wrappers,
        handlers=handlers,
        pre_hooks=pre_hooks,
        post_hooks=post_hooks,
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
    )


def add_exception_handler(  # noqa: PLR0913
    app: Starlette,
    logger: logging.Logger = logger_,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    handlers: dict[Exception, Handler] | None = None,
    pre_hooks: list[PreHook] | None = None,
    post_hooks: list[PostHook] | None = None,
    *,
    strip_debug: bool = False,
    strip_debug_codes: list[int] | None = None,
) -> None:
    eh = generate_handler(
        logger,
        cors,
        unhandled_wrappers,
        handlers,
        pre_hooks,
        post_hooks,
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
    )
    app.add_exception_handler(Exception, eh)
    app.add_exception_handler(HTTPException, eh)
