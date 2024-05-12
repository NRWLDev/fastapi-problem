import http
import json
from unittest import mock

import httpx
import pytest
from starlette.applications import Starlette
from starlette.exceptions import HTTPException

from fastapi_problem import error
from fastapi_problem.cors import CorsConfiguration
from fastapi_problem.handler import starlette


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
    def test_starlette_error(self):
        request = mock.Mock()
        exc = HTTPException(http.HTTPStatus.NOT_FOUND, "something bad")

        eh = starlette.generate_handler()
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.NOT_FOUND
        assert json.loads(response.body) == {
            "title": "Not Found",
            "details": exc.detail,
            "type": "http-not-found",
            "status": 404,
        }

    def test_starlette_error_with_headers(self):
        request = mock.Mock()
        exc = HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

        eh = starlette.generate_handler()
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.UNAUTHORIZED
        assert json.loads(response.body) == {
            "title": "Unauthorized",
            "details": exc.detail,
            "type": "http-unauthorized",
            "status": 401,
        }
        assert response.headers["www-authenticate"] == "Basic"

    def test_error_with_no_origin(self, cors):
        request = mock.Mock(headers={})
        exc = SomethingWrongError("something bad")

        eh = starlette.generate_handler(cors=cors)
        response = eh(request, exc)

        assert "access-control-allow-origin" not in response.headers

    def test_error_with_origin(self, cors):
        request = mock.Mock(headers={"origin": "localhost"})
        exc = SomethingWrongError("something bad")

        eh = starlette.generate_handler(cors=cors)
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"

    def test_error_with_origin_and_cookie(self, cors):
        request = mock.Mock(headers={"origin": "localhost", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        eh = starlette.generate_handler(cors=cors)
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"

    def test_missing_token_with_origin_limited_origins(self, cors):
        request = mock.Mock(headers={"origin": "localhost", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        cors.allow_origins = ["localhost"]

        eh = starlette.generate_handler(cors=cors)
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"

    def test_missing_token_with_origin_limited_origins_no_match(self, cors):
        request = mock.Mock(headers={"origin": "localhost2", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        cors.allow_origins = ["localhost"]

        eh = starlette.generate_handler(cors=cors)
        response = eh(request, exc)

        assert "access-control-allow-origin" not in response.headers


async def test_exception_handler_in_app():
    exception_handler = starlette.generate_handler(
        unhandled_wrappers={
            "default": CustomUnhandledException,
        },
    )

    app = Starlette(
        exception_handlers={
            Exception: exception_handler,
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


async def test_exception_handler_in_app_register():
    app = Starlette()
    starlette.add_exception_handler(
        app,
        unhandled_wrappers={
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
