import http
import json
from unittest import mock

import pytest

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
        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = base.ExceptionHandler(
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
