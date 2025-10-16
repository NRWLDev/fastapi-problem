from __future__ import annotations

import json
import typing as t
from http.client import responses
from warnings import warn

import rfc9457
from fastapi.exceptions import RequestValidationError
from rfc9457.openapi import problem_component, problem_response
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


def _generate_swagger_response(
    *exceptions: type[Problem] | Problem,
    documentation_uri_template: str = "",
    strict: bool = False,
) -> dict:
    examples = []
    for e in exceptions:
        exc = e("Additional error context.") if not isinstance(e, Problem) else e
        examples.append(exc.marshal(uri=documentation_uri_template, strict=strict))
    return problem_response(
        responses[exceptions[0].status],
        examples=examples,
    )


def generate_swagger_response(
    *exceptions: type[Problem] | Problem,
    documentation_uri_template: str = "",
    strict: bool = False,
) -> dict:
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
    def generate_swagger_response(self, *exceptions: type[Problem] | Problem) -> dict:
        return _generate_swagger_response(
            *exceptions,
            documentation_uri_template=self.documentation_uri_template,
            strict=self.strict,
        )


def customise_openapi(
    func: t.Callable[..., dict],
    *,
    documentation_uri_template: str = "",
    strict: bool = False,
    generic_defaults: bool = True,
) -> t.Callable[..., dict]:
    """Customize OpenAPI schema."""

    def wrapper() -> dict:
        """Wrapper."""
        res = func()

        if not res["paths"]:
            # If there are no paths, we don't need to add any responses
            return res

        if "components" not in res:
            res["components"] = {"schemas": {}}
        elif "schemas" not in res["components"]:
            res["components"]["schemas"] = {}

        validation_error = problem_component(
            "RequestValidationError",
            required=["errors"],
            errors={
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/ValidationError",
                },
            },
        )
        problem = problem_component("Problem")

        res["components"]["schemas"]["HTTPValidationError"] = validation_error
        res["components"]["schemas"]["Problem"] = problem

        for methods in res["paths"].values():
            for details in methods.values():
                if (
                    "422" in details["responses"]
                    and "application/problem+json" not in details["responses"]["422"]["content"]
                ):
                    details["responses"]["422"]["content"]["application/problem+json"] = details["responses"]["422"][
                        "content"
                    ].pop("application/json")
                if generic_defaults:
                    user_error = Problem(
                        "User facing error message.",
                        type_="client-error-type",
                        status=400,
                        detail="Additional error context.",
                    )
                    server_error = Problem(
                        "User facing error message.",
                        type_="server-error-type",
                        status=500,
                        detail="Additional error context.",
                    )
                    details["responses"]["4XX"] = problem_response(
                        description="Client Error",
                        examples=[user_error.marshal(uri=documentation_uri_template, strict=strict)],
                    )
                    details["responses"]["5XX"] = problem_response(
                        description="Server Error",
                        examples=[server_error.marshal(uri=documentation_uri_template, strict=strict)],
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
    eh: ExceptionHandler | None = None,
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
    app.openapi = customise_openapi(
        app.openapi,
        generic_defaults=generic_swagger_defaults,
        documentation_uri_template=eh.documentation_uri_template,
        strict=eh.strict,
    )

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
