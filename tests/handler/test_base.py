import http
import json
from unittest import mock

import pytest
from starlette.exceptions import HTTPException

from fastapi_problem import error
from fastapi_problem.cors import CorsConfiguration
from fastapi_problem.handler import base


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
    def test_unexpected_error_replaces_code(self):
        logger = mock.Mock()

        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = base.ExceptionHandler(
            logger=logger,
            unhandled_wrappers={
                "default": CustomUnhandledException,
            },
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "details": "Something went bad",
            "type": "custom-unhandled-exception",
            "status": 500,
        }
        assert logger.exception.call_args == mock.call(
            "Unhandled exception occurred.",
            exc_info=(type(exc), exc, None),
        )

    def test_strip_debug(self):
        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = base.ExceptionHandler(
            strip_debug=True,
            unhandled_wrappers={
                "default": CustomUnhandledException,
            },
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "type": "custom-unhandled-exception",
            "status": 500,
        }

    def test_strip_debug_with_code(self):
        logger = mock.Mock()
        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = base.ExceptionHandler(
            logger=logger,
            strip_debug=False,
            strip_debug_codes=[500],
            unhandled_wrappers={
                "default": CustomUnhandledException,
            },
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "type": "custom-unhandled-exception",
            "status": 500,
        }
        assert logger.debug.call_args_list == [
            mock.call("Stripping debug information from exception."),
            mock.call("Removed details: Something went bad"),
        ]

    def test_strip_debug_with_allowed_code(self):
        request = mock.Mock()
        exc = SomethingWrongError("something bad")

        eh = base.ExceptionHandler(
            strip_debug=False,
            strip_debug_codes=[400],
            unhandled_wrappers={
                "default": CustomUnhandledException,
            },
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "This is an error.",
            "type": "something-wrong",
            "details": "something bad",
            "status": 500,
        }

    def test_unexpected_error(self):
        logger = mock.Mock()

        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = base.ExceptionHandler(logger=logger)
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "details": "Something went bad",
            "type": "unhandled-exception",
            "status": 500,
        }
        assert logger.exception.call_args == mock.call(
            "Unhandled exception occurred.",
            exc_info=(type(exc), exc, None),
        )

    def test_error_handler(self):
        def pass_handler(_eh, _request, _exc):
            return None

        def handler(_eh, _request, exc):
            return error.Problem(
                title="Handled",
                type_="handled-error",
                details=str(exc),
                status=500,
                headers=None,
            )

        request = mock.Mock()
        exc = RuntimeError("Something went bad")

        eh = base.ExceptionHandler(handlers={RuntimeError: pass_handler, Exception: handler})
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Handled",
            "details": "Something went bad",
            "type": "handled-error",
            "status": 500,
        }

    def test_error_handler_pass(self):
        logger = mock.Mock()

        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = base.ExceptionHandler(logger=logger)
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "details": "Something went bad",
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

        eh = base.ExceptionHandler(handlers={HTTPException: base.http_exception_handler})
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.NOT_FOUND
        assert json.loads(response.body) == {
            "title": "Not Found",
            "details": "Not Found",
            "type": "http-not-found",
            "status": 404,
        }

    def test_known_error(self):
        request = mock.Mock()
        exc = SomethingWrongError("something bad")

        eh = base.ExceptionHandler()
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "This is an error.",
            "details": "something bad",
            "type": "something-wrong",
            "status": 500,
        }

    def test_error_with_no_origin(self, cors):
        request = mock.Mock(headers={})
        exc = SomethingWrongError("something bad")

        eh = base.ExceptionHandler(post_hooks=[base.CorsPostHook(cors)])
        response = eh(request, exc)

        assert "access-control-allow-origin" not in response.headers

    def test_error_with_origin(self, cors):
        request = mock.Mock(headers={"origin": "localhost"})
        exc = SomethingWrongError("something bad")

        eh = base.ExceptionHandler(post_hooks=[base.CorsPostHook(cors)])
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"

    def test_error_with_origin_and_cookie(self, cors):
        request = mock.Mock(headers={"origin": "localhost", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        eh = base.ExceptionHandler(post_hooks=[base.CorsPostHook(cors)])
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"

    def test_missing_token_with_origin_limited_origins(self, cors):
        request = mock.Mock(headers={"origin": "localhost", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        cors.allow_origins = ["localhost"]

        eh = base.ExceptionHandler(post_hooks=[base.CorsPostHook(cors)])
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"

    def test_missing_token_with_origin_limited_origins_no_match(self, cors):
        request = mock.Mock(headers={"origin": "localhost2", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        cors.allow_origins = ["localhost"]

        eh = base.ExceptionHandler(post_hooks=[base.CorsPostHook(cors)])
        response = eh(request, exc)

        assert "access-control-allow-origin" not in response.headers
