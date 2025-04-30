import http
import json
from unittest import mock

import httpx
import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from fastapi_problem import error, handler
from fastapi_problem.cors import CorsConfiguration


class SomethingWrongError(error.ServerProblem):
    title = "This is an error."


class CustomUnhandledException(error.ServerProblem):
    title = "Unhandled exception occurred."


class CustomValidationError(error.StatusProblem):
    status = 422
    title = "Request validation error."


@pytest.fixture
def cors():
    return CorsConfiguration(
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )


class TestExceptionHandler:
    @pytest.mark.parametrize("default_key", ["default", "500"])
    def test_unexpected_error_replaces_code(self, default_key):
        logger = mock.Mock()

        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = handler.ExceptionHandler(
            logger=logger,
            unhandled_wrappers={
                default_key: CustomUnhandledException,
            },
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "detail": "Something went bad",
            "type": "custom-unhandled-exception",
            "status": 500,
        }
        assert logger.exception.call_args == mock.call(
            "Unhandled exception occurred.",
            exc_info=(type(exc), exc, None),
        )

    def test_documentation_uri_template(self):
        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = handler.ExceptionHandler(
            unhandled_wrappers={
                "default": CustomUnhandledException,
            },
            documentation_uri_template="https://docs/errors/{type}",
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "type": "https://docs/errors/custom-unhandled-exception",
            "status": 500,
            "detail": "Something went bad",
        }

    def test_strict(self):
        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = handler.ExceptionHandler(
            unhandled_wrappers={
                "default": CustomUnhandledException,
            },
            documentation_uri_template="https://docs/errors/{type}",
            strict_rfc9457=True,
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "type": "about:blank",
            "status": 500,
            "detail": "Something went bad",
        }

    def test_unexpected_error(self):
        logger = mock.Mock()

        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = handler.ExceptionHandler(logger=logger)
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "detail": "Something went bad",
            "type": "unhandled-exception",
            "status": 500,
        }
        assert logger.exception.call_args == mock.call(
            "Unhandled exception occurred.",
            exc_info=(type(exc), exc, None),
        )

    def test_error_handler_can_pass(self):
        def pass_handler(_eh, _request, _exc):
            return None

        def handler_(_eh, _request, exc):
            return error.Problem(
                title="Handled",
                type_="handled-error",
                detail=str(exc),
                status=500,
                headers=None,
            )

        request = mock.Mock()
        exc = RuntimeError("Something went bad")

        eh = handler.ExceptionHandler(handlers={RuntimeError: pass_handler, Exception: handler_})
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Handled",
            "detail": "Something went bad",
            "type": "handled-error",
            "status": 500,
        }

    def test_error_handler_breaks_at_first_bite(self):
        def handler_(_eh, _request, exc):
            return error.Problem(
                title="Handled",
                type_="handled-error",
                detail=str(exc),
                status=400,
                headers=None,
            )

        def unused_handler(_eh, _request, _exc):
            return error.Problem(
                title="Handled",
                type_="handled-error",
                detail=str(exc),
                status=500,
                headers=None,
            )

        request = mock.Mock()
        exc = RuntimeError("Something went bad")

        eh = handler.ExceptionHandler(handlers={RuntimeError: handler_, Exception: unused_handler})
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert json.loads(response.body) == {
            "title": "Handled",
            "detail": "Something went bad",
            "type": "handled-error",
            "status": 400,
        }

    def test_error_handler_pass(self):
        logger = mock.Mock()

        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = handler.ExceptionHandler(logger=logger)
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.headers["content-type"] == "application/problem+json"
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "detail": "Something went bad",
            "type": "unhandled-exception",
            "status": 500,
        }
        assert logger.exception.call_args == mock.call(
            "Unhandled exception occurred.",
            exc_info=(type(exc), exc, None),
        )

    def test_starlette_error(self):
        request = mock.Mock()
        exc = HTTPException(404)

        eh = handler.ExceptionHandler(handlers={HTTPException: handler.http_exception_handler_})
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.NOT_FOUND
        assert json.loads(response.body) == {
            "title": "Not Found",
            "detail": "Not Found",
            "type": "http-not-found",
            "status": 404,
        }

    def test_starlette_error_custom_wrapper(self):
        request = mock.Mock()
        exc = HTTPException(404)

        eh = handler.ExceptionHandler(
            handlers={HTTPException: handler.http_exception_handler_},
            unhandled_wrappers={
                "404": SomethingWrongError,
            },
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "This is an error.",
            "detail": "Not Found",
            "type": "something-wrong",
            "status": 500,
        }

    def test_known_error(self):
        request = mock.Mock()
        exc = SomethingWrongError("something bad")

        eh = handler.ExceptionHandler()
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "This is an error.",
            "detail": "something bad",
            "type": "something-wrong",
            "status": 500,
        }

    def test_error_with_no_origin(self, cors):
        app = FastAPI()
        request = mock.Mock(headers={})
        exc = SomethingWrongError("something bad")

        eh = handler.add_exception_handler(
            app=app,
            cors=cors,
        )
        response = eh(request, exc)

        assert "access-control-allow-origin" not in response.headers

    def test_error_with_origin(self, cors):
        app = FastAPI()
        request = mock.Mock(headers={"origin": "localhost"})
        exc = SomethingWrongError("something bad")

        eh = handler.add_exception_handler(
            app=app,
            cors=cors,
        )
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"

    def test_error_with_origin_and_cookie(self, cors):
        app = FastAPI()
        request = mock.Mock(headers={"origin": "localhost", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        eh = handler.add_exception_handler(
            app=app,
            cors=cors,
        )
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"

    def test_missing_token_with_origin_limited_origins(self, cors):
        app = FastAPI()
        request = mock.Mock(headers={"origin": "localhost", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        cors.allow_origins = ["localhost"]

        eh = handler.add_exception_handler(
            app=app,
            cors=cors,
        )
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["vary"] == "Origin"
        assert response.headers["access-control-allow-origin"] == "localhost"

    def test_missing_token_with_origin_limited_origins_no_match(self, cors):
        app = FastAPI()
        request = mock.Mock(headers={"origin": "localhost2", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        cors.allow_origins = ["localhost"]

        eh = handler.add_exception_handler(
            app=app,
            cors=cors,
        )
        response = eh(request, exc)

        assert "access-control-allow-origin" not in response.headers

    def test_fastapi_error(self):
        app = FastAPI()
        request = mock.Mock()
        exc = RequestValidationError([])

        eh = handler.add_exception_handler(
            app=app,
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY
        assert json.loads(response.body) == {
            "title": "Request validation error.",
            "errors": [],
            "type": "request-validation-failed",
            "status": 422,
        }

    def test_fastapi_error_custom_wrapper(self):
        app = FastAPI()
        request = mock.Mock()
        exc = RequestValidationError([])

        eh = handler.add_exception_handler(
            app=app,
            unhandled_wrappers={
                "422": CustomValidationError,
            },
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY
        assert json.loads(response.body) == {
            "title": "Request validation error.",
            "errors": [],
            "type": "custom-validation",
            "status": 422,
        }

    def test_pre_hook(self):
        app = FastAPI()
        logger = mock.Mock()

        request = mock.Mock()
        exc = ValueError("Something went bad")

        def hook(_request, exc) -> None:
            logger.debug(str(type(exc)))

        eh = handler.add_exception_handler(
            app=app,
            logger=logger,
            pre_hooks=[hook],
        )
        eh(request, exc)

        assert logger.debug.call_args == mock.call("<class 'ValueError'>")


async def test_exception_handler_in_app():
    m = mock.Mock()

    def pre_hook(_req, _exc):
        m.call("pre-hook")

    app = FastAPI()
    eh = handler.new_exception_handler(
        pre_hooks=[pre_hook],
        unhandled_wrappers={
            "422": CustomValidationError,
            "default": CustomUnhandledException,
        },
    )
    handler.add_exception_handler(
        app=app,
        eh=eh,
    )

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, base_url="https://test")

    r = await client.get("/endpoint")
    assert r.json() == {
        "type": "http-not-found",
        "title": "Not Found",
        "detail": "Not Found",
        "status": 404,
    }
    assert m.call.call_args == mock.call("pre-hook")


async def test_exception_handler_in_app_post_register():
    app = FastAPI()

    handler.add_exception_handler(
        app,
        unhandled_wrappers={
            "422": CustomValidationError,
            "default": CustomUnhandledException,
        },
    )

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, base_url="https://test")

    r = await client.get("/endpoint")
    assert r.json() == {
        "type": "http-not-found",
        "title": "Not Found",
        "detail": "Not Found",
        "status": 404,
    }


def test_swagger_problem_response():
    assert handler._swagger_problem_response(
        description="Client Error",
        examples=[
            error.Problem(
                title="User facing error message.",
                type_="client-error-type",
                status=400,
                detail="Additional error context.",
            ).marshal(),
        ],
    ) == {
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "example": {
                    "title": "User facing error message.",
                    "detail": "Additional error context.",
                    "type": "client-error-type",
                    "status": 400,
                },
            },
        },
        "description": "Client Error",
    }


def test_swagger_problem_response_multiple_examples():
    assert handler._swagger_problem_response(
        description="Client Error",
        examples=[
            error.Problem(
                title="User facing error message.",
                type_="client-error-type",
                status=400,
                detail="Additional error context.",
            ).marshal(),
            error.Problem(
                title="Another user facing error message.",
                type_="another-client-error-type",
                status=400,
                detail="Additional error context.",
            ).marshal(),
        ],
    ) == {
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "examples": {
                    "User facing error message.": {
                        "value": {
                            "title": "User facing error message.",
                            "detail": "Additional error context.",
                            "type": "client-error-type",
                            "status": 400,
                        },
                    },
                    "Another user facing error message.": {
                        "value": {
                            "title": "Another user facing error message.",
                            "detail": "Additional error context.",
                            "type": "another-client-error-type",
                            "status": 400,
                        },
                    },
                },
            },
        },
        "description": "Client Error",
    }


def test_generate_swagger_response_status_problem_deprecated():
    assert handler.generate_swagger_response(error.BadRequestProblem) == {
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "example": {
                    "title": "Base http exception.",
                    "detail": "Additional error context.",
                    "type": "bad-request-problem",
                    "status": 400,
                },
            },
        },
        "description": "Bad Request",
    }


def test_generate_swagger_response_instantiated_problem():
    eh = handler.new_exception_handler()
    assert eh.generate_swagger_response(error.BadRequestProblem("Custom detail", additional="key")) == {
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "example": {
                    "title": "Base http exception.",
                    "detail": "Custom detail",
                    "type": "bad-request-problem",
                    "status": 400,
                    "additional": "key",
                },
            },
        },
        "description": "Bad Request",
    }


def test_generate_swagger_response_status_problem():
    eh = handler.new_exception_handler()
    assert eh.generate_swagger_response(error.BadRequestProblem) == {
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "example": {
                    "title": "Base http exception.",
                    "detail": "Additional error context.",
                    "type": "bad-request-problem",
                    "status": 400,
                },
            },
        },
        "description": "Bad Request",
    }


def test_generate_swagger_response_custom_problem():
    eh = handler.new_exception_handler()
    assert eh.generate_swagger_response(CustomUnhandledException) == {
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "example": {
                    "title": "Unhandled exception occurred.",
                    "detail": "Additional error context.",
                    "type": "custom-unhandled-exception",
                    "status": 500,
                },
            },
        },
        "description": "Internal Server Error",
    }


def test_generate_swagger_response_multiple_problems():
    eh = handler.new_exception_handler()
    assert eh.generate_swagger_response(CustomUnhandledException, error.ServerProblem) == {
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "examples": {
                    "Base http exception.": {
                        "value": {
                            "title": "Base http exception.",
                            "detail": "Additional error context.",
                            "type": "server-problem",
                            "status": 500,
                        },
                    },
                    "Unhandled exception occurred.": {
                        "value": {
                            "title": "Unhandled exception occurred.",
                            "detail": "Additional error context.",
                            "type": "custom-unhandled-exception",
                            "status": 500,
                        },
                    },
                },
            },
        },
        "description": "Internal Server Error",
    }


def test_generate_swagger_response_status_problem_with_uri_template():
    eh = handler.new_exception_handler(
        documentation_uri_template="https://docs/errors/{type}",
    )
    assert eh.generate_swagger_response(error.BadRequestProblem) == {
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "example": {
                    "title": "Base http exception.",
                    "detail": "Additional error context.",
                    "type": "https://docs/errors/bad-request-problem",
                    "status": 400,
                },
            },
        },
        "description": "Bad Request",
    }


def test_generate_swagger_response_status_problem_strict():
    eh = handler.new_exception_handler(
        documentation_uri_template="https://docs/errors/{type}",
        strict_rfc9457=True,
    )
    assert eh.generate_swagger_response(error.BadRequestProblem) == {
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "#/components/schemas/Problem",
                },
                "example": {
                    "title": "Base http exception.",
                    "detail": "Additional error context.",
                    "type": "about:blank",
                    "status": 400,
                },
            },
        },
        "description": "Bad Request",
    }


async def test_customise_openapi():
    app = FastAPI()

    app.openapi = handler.customise_openapi(app.openapi)

    @app.get("/status")
    async def status(_a: str) -> dict:
        return {}

    app.openapi()
    res = app.openapi()  # ensure openapi can be called repeatedly
    assert res["components"]["schemas"]["HTTPValidationError"] == {
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
    assert "Problem" in res["components"]["schemas"]
    assert "ValidationError" in res["components"]["schemas"]

    assert res["paths"]["/status"]["get"]["responses"] == {
        "200": {
            "content": {
                "application/json": {
                    "schema": {
                        "title": "Response Status Status Get",
                        "type": "object",
                    },
                },
            },
            "description": "Successful Response",
        },
        "422": {
            "content": {
                "application/problem+json": {
                    "schema": {
                        "$ref": "#/components/schemas/HTTPValidationError",
                    },
                },
            },
            "description": "Validation Error",
        },
        "4XX": {
            "content": {
                "application/problem+json": {
                    "schema": {
                        "$ref": "#/components/schemas/Problem",
                    },
                    "example": {
                        "title": "User facing error message.",
                        "detail": "Additional error context.",
                        "type": "client-error-type",
                        "status": 400,
                    },
                },
            },
            "description": "Client Error",
        },
        "5XX": {
            "content": {
                "application/problem+json": {
                    "schema": {
                        "$ref": "#/components/schemas/Problem",
                    },
                    "example": {
                        "title": "User facing error message.",
                        "detail": "Additional error context.",
                        "type": "server-error-type",
                        "status": 500,
                    },
                },
            },
            "description": "Server Error",
        },
    }


async def test_customise_openapi_handles_no_components():
    app = FastAPI()

    app.openapi = handler.customise_openapi(app.openapi)

    res = app.openapi()
    assert res["paths"] == {}
    assert "components" not in res


async def test_customise_openapi_generic_opt_out():
    app = FastAPI()

    app.openapi = handler.customise_openapi(app.openapi, generic_defaults=False)

    @app.get("/status")
    async def status(_a: str) -> dict:
        return {}

    res = app.openapi()
    assert res["components"]["schemas"]["HTTPValidationError"] == {
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
    assert "Problem" in res["components"]["schemas"]
    assert "ValidationError" in res["components"]["schemas"]

    assert res["paths"]["/status"]["get"]["responses"] == {
        "200": {
            "content": {
                "application/json": {
                    "schema": {
                        "title": "Response Status Status Get",
                        "type": "object",
                    },
                },
            },
            "description": "Successful Response",
        },
        "422": {
            "content": {
                "application/problem+json": {
                    "schema": {
                        "$ref": "#/components/schemas/HTTPValidationError",
                    },
                },
            },
            "description": "Validation Error",
        },
    }


async def test_custom_http_exception_handler_in_app():
    def custom_handler(_eh, _request, _exc) -> error.Problem:
        return error.Problem("a problem")

    app = FastAPI()

    handler.add_exception_handler(
        app=app,
        http_exception_handler=custom_handler,
    )

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, base_url="https://test")

    r = await client.get("/endpoint")
    assert r.json() == {
        "type": "problem",
        "title": "a problem",
        "status": 500,
    }
