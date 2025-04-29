from __future__ import annotations

import json
import typing as t
from http.client import responses
from warnings import warn

import rfc9457
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette_problem.handler import (
    CorsPostHook,
    Handler,
    PostHook,
    PreHook,
    StripExtrasPostHook,
    http_exception_handler_,
)
from starlette_problem.handler import ExceptionHandler as BaseExceptionHandler

from fastapi_problem.error import Problem, StatusProblem

if t.TYPE_CHECKING:
    import logging

    from fastapi import FastAPI
    from starlette.requests import Request

    from fastapi_problem.cors import CorsConfiguration


class Example(t.NamedTuple):
    title: str
    type_: str
    status: int


def _swagger_problem_response(description: str, examples: list[Example]) -> dict:
    examples_ = {
        ex.title: {
            "value": {
                "title": ex.title,
                "detail": "Additional error context.",
                "type": ex.type_,
                "status": ex.status,
            },
        }
        for ex in examples
    }
    ret_val = {
        "description": description,
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
            },
        },
    }
    key = "examples" if len(examples) > 1 else "example"
    ret_val["content"]["application/problem+json"][key] = (
        examples_ if len(examples) > 1 else examples_[examples[0].title]["value"]
    )

    return ret_val


def _generate_swagger_response(
    *exceptions: Problem,
    documentation_uri_template: str = "",
    strict: bool = False,
) -> dict:
    examples = []
    for e in exceptions:
        exc = e("Additional error context.")
        d = exc.marshal(uri=documentation_uri_template, strict=strict)
        examples.append(
            Example(
                title=d["title"],
                type_=d["type"],
                status=d["status"],
            ),
        )
    return _swagger_problem_response(
        responses[examples[0].status],
        examples=examples,
    )


def generate_swagger_response(*exceptions: Problem, documentation_uri_template: str = "", strict: bool = False) -> dict:
    warn(
        "Direct calls to generate_swagger_response are being deprecated, use `eh.generate_swagger_response(...)` instead.",
        FutureWarning,
        stacklevel=2,
    )
    return _generate_swagger_response(
        *exceptions,
        documentation_uri_template=documentation_uri_template,
        strict=strict,
    )


class ExceptionHandler(BaseExceptionHandler):
    def generate_swagger_response(self, *exceptions: Problem) -> dict:
        return _generate_swagger_response(
            *exceptions,
            documentation_uri_template=self.documentation_uri_template,
            strict=self.strict,
        )


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
            "title": "RequestValidationError",
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
                    if (
                        "422" in details["responses"]
                        and "application/problem+json" not in details["responses"]["422"]["content"]
                    ):
                        details["responses"]["422"]["content"]["application/problem+json"] = details["responses"][
                            "422"
                        ]["content"].pop("application/json")
                    details["responses"]["4XX"] = _swagger_problem_response(
                        description="Client Error",
                        examples=[
                            Example(
                                title="User facing error message.",
                                type_="client-error-type",
                                status=400,
                            ),
                        ],
                    )
                    details["responses"]["5XX"] = _swagger_problem_response(
                        description="Server Error",
                        examples=[
                            Example(
                                title="User facing error message.",
                                type_="server-error-type",
                                status=500,
                            ),
                        ],
                    )

        return res

    return wrapper


def request_validation_handler_(
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


def new_exception_handler(  # noqa: PLR0913
    logger: logging.Logger | None = None,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    handlers: dict[type[Exception], Handler] | None = None,
    pre_hooks: list[PreHook] | None = None,
    post_hooks: list[PostHook] | None = None,
    documentation_uri_template: str = "",
    http_exception_handler: Handler = http_exception_handler_,
    request_validation_handler: Handler = request_validation_handler_,
    *,
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

    return ExceptionHandler(
        logger=logger,
        unhandled_wrappers=unhandled_wrappers,
        handlers=handlers,
        pre_hooks=pre_hooks,
        post_hooks=post_hooks,
        documentation_uri_template=documentation_uri_template,
        strict_rfc9457=strict_rfc9457,
    )


def add_exception_handler(  # noqa: PLR0913
    app: FastAPI,
    eh: ExceptionHandler or None = None,
    *,
    logger: logging.Logger | None = None,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    handlers: dict[type[Exception], Handler] | None = None,
    pre_hooks: list[PreHook] | None = None,
    post_hooks: list[PostHook] | None = None,
    documentation_uri_template: str = "",
    http_exception_handler: Handler = http_exception_handler_,
    request_validation_handler: Handler = request_validation_handler_,
    generic_swagger_defaults: bool = True,
    strict_rfc9457: bool = False,
) -> ExceptionHandler:
    if eh is None:
        warn(
            "Generating exception handler while adding is being deprecated, use `new_exception_handler(...)`..",
            FutureWarning,
            stacklevel=2,
        )

        eh = new_exception_handler(
            logger=logger,
            cors=cors,
            unhandled_wrappers=unhandled_wrappers,
            handlers=handlers,
            pre_hooks=pre_hooks,
            post_hooks=post_hooks,
            documentation_uri_template=documentation_uri_template,
            http_exception_handler=http_exception_handler,
            request_validation_handler=request_validation_handler,
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
    "new_exception_handler",
    "add_exception_handler",
    "http_exception_handler_",
    "request_validation_handler_",
]
