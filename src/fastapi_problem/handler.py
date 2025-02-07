from __future__ import annotations

import json
import typing as t

import rfc9457
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette_problem.handler import (
    CorsPostHook,
    ExceptionHandler,
    Handler,
    PostHook,
    PreHook,
    StripExtrasPostHook,
    http_exception_handler,
)

from fastapi_problem.error import Problem, StatusProblem

if t.TYPE_CHECKING:
    import logging

    from fastapi import FastAPI
    from starlette.requests import Request

    from fastapi_problem.cors import CorsConfiguration


def customise_openapi(func: t.Callable[..., dict], *, generic_defaults: bool = True) -> t.Callable[..., dict]:
    """Customize OpenAPI schema."""

    def wrapper() -> dict:
        """Wrapper."""
        res = func()

        if "components" not in res:
            return res

        validation_error = {
            "properties": {
                "title": {
                    "type": "string",
                    "title": "Problem Title",
                },
                "type": {
                    "type": "string",
                    "title": "Problem type",
                },
                "status": {
                    "type": "integer",
                    "title": "Status code",
                },
                "errors": {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/ValidationError",
                    },
                },
            },
            "type": "object",
            "required": [
                "type",
                "title",
                "errors",
                "status",
            ],
            "title": "ValidationError",
        }
        problem = {
            "properties": {
                "title": {
                    "type": "string",
                    "title": "Problem Title",
                },
                "type": {
                    "type": "string",
                    "title": "Problem type",
                },
                "status": {
                    "type": "integer",
                    "title": "Status code",
                },
                "detail": {
                    "anyOf": [
                        {
                            "type": "string",
                        },
                        {
                            "type": "null",
                        },
                    ],
                    "title": "Problem detail",
                },
            },
            "example": {
                "title": "Request validation error.",
                "errors": [],
                "type": "request-validation-failed",
                "status": 422,
            },
            "type": "object",
            "required": [
                "type",
                "title",
                "detail",
                "status",
            ],
            "title": "Problem",
        }

        res["components"]["schemas"]["HTTPValidationError"] = validation_error
        res["components"]["schemas"]["Problem"] = problem

        if generic_defaults:
            for methods in res["paths"].values():
                for details in methods.values():
                    details["responses"]["4XX"] = {
                        "description": "Client Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Problem",
                                },
                                "example": {
                                    "title": "User facing error message.",
                                    "details": "Additional error context.",
                                    "type": "client-error-type",
                                    "status": 400,
                                },
                            },
                        },
                    }
                    details["responses"]["5XX"] = {
                        "description": "Server Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Problem",
                                },
                                "example": {
                                    "title": "User facing error message.",
                                    "details": "Additional error context.",
                                    "type": "server-error-type",
                                    "status": 500,
                                },
                            },
                        },
                    }

        return res

    return wrapper


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


def add_exception_handler(  # noqa: PLR0913
    app: FastAPI,
    logger: logging.Logger | None = None,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    handlers: dict[type[Exception], Handler] | None = None,
    pre_hooks: list[PreHook] | None = None,
    post_hooks: list[PostHook] | None = None,
    documentation_uri_template: str = "",
    *,
    generic_swagger_defaults: bool = True,
    strict_rfc9457: bool = False,
) -> ExceptionHandler:
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

    eh = ExceptionHandler(
        logger=logger,
        unhandled_wrappers=unhandled_wrappers,
        handlers=handlers,
        pre_hooks=pre_hooks,
        post_hooks=post_hooks,
        documentation_uri_template=documentation_uri_template,
        strict_rfc9457=strict_rfc9457,
    )

    app.add_exception_handler(Exception, eh)
    app.add_exception_handler(rfc9457.Problem, eh)
    app.add_exception_handler(HTTPException, eh)
    app.add_exception_handler(RequestValidationError, eh)

    # Override default 422 with Problem schema
    app.openapi = customise_openapi(app.openapi, generic_defaults=generic_swagger_defaults)

    return eh


__all__ = [
    "CorsPostHook",
    "ExceptionHandler",
    "Handler",
    "PostHook",
    "PreHook",
    "StripExtrasPostHook",
    "add_exception_handler",
    "http_exception_handler",
]
