from __future__ import annotations

import json
import typing as t

import rfc9457
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette_problem.handler import CorsPostHook, ExceptionHandler, Handler, PostHook, PreHook, http_exception_handler

from fastapi_problem.error import Problem, StatusProblem

if t.TYPE_CHECKING:
    import logging

    from fastapi import FastAPI
    from starlette.requests import Request

    from fastapi_problem.cors import CorsConfiguration


def request_validation_handler(
    eh: ExceptionHandler,
    _request: Request,
    exc: RequestValidationError,
) -> Problem:
    wrapper = eh.unhandled_wrappers.get("422")
    errors = json.loads(json.dumps(exc.errors(), default=str))
    kwargs = {"errors": errors}
    return (
        wrapper(**kwargs)
        if wrapper
        else Problem(
            title="Request validation error.",
            type_="request-validation-failed",
            status=422,
            **kwargs,
        )
    )


def generate_handler(  # noqa: PLR0913
    logger: logging.Logger | None = None,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    handlers: dict[type[Exception], Handler] | None = None,
    pre_hooks: list[PreHook] | None = None,
    post_hooks: list[PostHook] | None = None,
    documentation_base_url: str | None = None,
    *,
    strip_debug: bool = False,
    strip_debug_codes: list[int] | None = None,
) -> t.Callable:
    handlers = handlers or {}
    handlers.update(
        {
            HTTPException: http_exception_handler,
            RequestValidationError: request_validation_handler,
        },
    )
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
        documentation_base_url=documentation_base_url,
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
    )


def add_exception_handler(  # noqa: PLR0913
    app: FastAPI,
    logger: logging.Logger | None = None,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    handlers: dict[type[Exception], Handler] | None = None,
    pre_hooks: list[PreHook] | None = None,
    post_hooks: list[PostHook] | None = None,
    documentation_base_url: str | None = None,
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
        documentation_base_url,
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
    )

    app.add_exception_handler(Exception, eh)
    app.add_exception_handler(rfc9457.Problem, eh)
    app.add_exception_handler(HTTPException, eh)
    app.add_exception_handler(RequestValidationError, eh)


__all__ = [
    "add_exception_handler",
    "http_exception_handler",
    "generate_handler",
    "ExceptionHandler",
    "Handler",
    "PreHook",
    "PostHook",
]
