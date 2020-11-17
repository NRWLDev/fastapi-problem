import json
from unittest import mock

from web_error import error
from web_error.handler import fastapi


class ATestError(error.ServerException):
    message = "This is an error."
    code = "E123"


class TestExceptionHandler:
    def test_unexpected_error(self, monkeypatch):
        monkeypatch.setattr(fastapi.logger, "exception", mock.Mock())

        request = mock.Mock()
        exc = Exception("Something went bad")

        response = fastapi.exception_handler(request, exc)

        assert response.status_code == 500
        assert json.loads(response.body) == {
            "message": "Unhandled exception occured.", "debug_message": "Something went bad", "code": None,
        }
        assert fastapi.logger.exception.call_args == mock.call("Unhandled exception occured.")

    def test_known_error(self):
        request = mock.Mock()
        exc = ATestError("something bad")

        response = fastapi.exception_handler(request, exc)

        assert response.status_code == 500
        assert json.loads(response.body) == {
            "message": "This is an error.", "debug_message": "something bad", "code": "E123",
        }
