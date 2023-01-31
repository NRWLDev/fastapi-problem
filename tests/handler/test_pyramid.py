from unittest import mock

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPServerError

from web_error import error
from web_error.handler import pyramid


class ATestError(error.ServerException):
    message = "This is an error."
    code = "E123"


class TestPyramidHandler:
    def test_server_error(self, monkeypatch):
        monkeypatch.setattr(pyramid.logger, "exception", mock.Mock())

        request = testing.DummyRequest()
        exc = HTTPServerError(detail="detail", explanation="explanation")

        response = pyramid.pyramid_handler(exc, request)

        assert request.response.status == "500 Internal Server Error"
        assert response == {"message": "explanation", "debug_message": "detail", "code": None}
        assert pyramid.logger.exception.call_args == mock.call("explanation")

    def test_user_error(self):
        request = testing.DummyRequest()
        exc = HTTPNotFound(detail="/not_found")

        response = pyramid.pyramid_handler(exc, request)

        assert request.response.status == "404 Not Found"
        assert response == {"message": "The resource could not be found.", "debug_message": "/not_found", "code": None}

    def test_method_not_allowed(self):
        request = testing.DummyRequest()
        exc = HTTPNotFound(detail="predicate mismatch for view note (request_method = DELETE)'")

        response = pyramid.pyramid_handler(exc, request)

        assert request.response.status == "405 Method Not Allowed"
        assert response == {
            "message": "Request method not allowed.",
            "debug_message": "predicate mismatch for view note (request_method = DELETE)'",
            "code": None,
        }


class TestExceptionHandler:
    def test_unexpected_error(self, monkeypatch):
        monkeypatch.setattr(pyramid.logger, "exception", mock.Mock())

        request = testing.DummyRequest()
        exc = Exception("Something went bad")

        response = pyramid.exception_handler(exc, request)

        assert request.response.status == "500 Internal Server Error"
        assert response == {
            "message": "Unhandled exception occurred.", "debug_message": "Something went bad", "code": None,
        }
        assert pyramid.logger.exception.call_args == mock.call("Unhandled exception occurred.")

    def test_known_error(self):
        request = testing.DummyRequest()
        exc = ATestError("something bad")

        response = pyramid.exception_handler(exc, request)

        assert request.response.status == "500 Internal Server Error"
        assert response == {"message": "This is an error.", "debug_message": "something bad", "code": "E123"}
