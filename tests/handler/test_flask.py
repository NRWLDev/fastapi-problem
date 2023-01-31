from unittest import mock

from werkzeug.exceptions import NotFound

from web_error import error
from web_error.handler import flask


class ATestError(error.BadRequestException):
    message = "This is an error."
    code = "E123"


class TestExceptionHandler:
    def test_unexpected_error(self, monkeypatch):
        monkeypatch.setattr(flask.logger, "exception", mock.Mock())

        exc = Exception("Something went bad")

        response = flask.exception_handler(exc)

        assert response.status == "500 INTERNAL SERVER ERROR"
        assert response.json == {
            "message": "Unhandled exception occurred.", "debug_message": "Something went bad", "code": None,
        }
        assert flask.logger.exception.call_args == mock.call("Unhandled exception occurred.")

    def test_flask_error(self):
        exc = NotFound("something bad")

        response = flask.exception_handler(exc)

        assert response.status == "404 NOT FOUND"
        assert response.json == {"message": "Not Found", "debug_message": "something bad", "code": None}

    def test_known_error(self):
        exc = ATestError("something bad")

        response = flask.exception_handler(exc)

        assert response.status == "400 BAD REQUEST"
        assert response.json == {"message": "This is an error.", "debug_message": "something bad", "code": "E123"}
