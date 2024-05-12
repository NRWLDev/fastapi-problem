import http
import json
from unittest import mock

import httpx
import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from fastapi_problem import error
from fastapi_problem.cors import CorsConfiguration
from fastapi_problem.handler import fastapi


class SomethingWrongError(error.ServerProblem):
    title = "This is an error."


class CustomUnhandledException(error.ServerProblem):
    title = "Unhandled exception occurred."


class CustomValidationError(error.StatusProblem):
    status = 422
    title = "Request validation error."


@pytest.fixture()
def cors():
    return CorsConfiguration(
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )


class TestExceptionHandler:
    def test_fastapi_error(self):
        request = mock.Mock()
        exc = RequestValidationError([])

        eh = fastapi.generate_handler(
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

    def test_error_with_origin(self, cors):
        request = mock.Mock(headers={"origin": "localhost"})
        exc = SomethingWrongError("something bad")

        eh = fastapi.generate_handler(cors=cors)
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"

    def test_error_with_origin_and_cookie(self, cors):
        request = mock.Mock(headers={"origin": "localhost", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        eh = fastapi.generate_handler(cors=cors)
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"

    def test_missing_token_with_origin_limited_origins(self, cors):
        request = mock.Mock(headers={"origin": "localhost", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        cors.allow_origins = ["localhost"]

        eh = fastapi.generate_handler(cors=cors)
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"

    def test_missing_token_with_origin_limited_origins_no_match(self, cors):
        request = mock.Mock(headers={"origin": "localhost2", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        cors.allow_origins = ["localhost"]

        eh = fastapi.generate_handler(cors=cors)
        response = eh(request, exc)

        assert "access-control-allow-origin" not in response.headers


async def test_exception_handler_in_app():
    exception_handler = fastapi.generate_handler(
        unhandled_wrappers={
            "422": CustomValidationError,
            "default": CustomUnhandledException,
        },
    )

    app = FastAPI(
        exception_handlers={
            Exception: exception_handler,
            RequestValidationError: exception_handler,
            HTTPException: exception_handler,
        },
    )
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, app=app, base_url="https://test")

    r = await client.get("/endpoint")
    assert r.json() == {
        "type": "http-not-found",
        "title": "Not Found",
        "details": "Not Found",
        "status": 404,
    }


async def test_exception_handler_in_app_post_register():
    app = FastAPI()

    fastapi.add_exception_handler(
        app,
        unhandled_wrappers={
            "422": CustomValidationError,
            "default": CustomUnhandledException,
        },
    )

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, app=app, base_url="https://test")

    r = await client.get("/endpoint")
    assert r.json() == {
        "type": "http-not-found",
        "title": "Not Found",
        "details": "Not Found",
        "status": 404,
    }
