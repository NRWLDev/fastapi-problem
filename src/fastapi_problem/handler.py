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
    documentation_base_uri: str = "",
    *,
    strip_debug: bool = False,
    strip_debug_codes: list[int] | None = None,
    strict_rfc9457: bool = False,
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
        # Ensure it runs first before any custom modifications
        post_hooks.insert(0, CorsPostHook(cors))

    return ExceptionHandler(
        logger=logger,
        unhandled_wrappers=unhandled_wrappers,
        handlers=handlers,
        pre_hooks=pre_hooks,
        post_hooks=post_hooks,
        documentation_base_url=documentation_base_url,
        documentation_base_uri=documentation_base_uri,
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
        strict_rfc9457=strict_rfc9457,
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
    documentation_base_uri: str = "",
    *,
    strip_debug: bool = False,
    strip_debug_codes: list[int] | None = None,
    strict_rfc9457: bool = False,
) -> None:
    eh = generate_handler(
        logger,
        cors,
        unhandled_wrappers,
        handlers,
        pre_hooks,
        post_hooks,
        documentation_base_url,
        documentation_base_uri,
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
        strict_rfc9457=strict_rfc9457,
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
