import pytest

from web_error import error


class NotFoundError(error.NotFoundException):
    title = "a 404 message"


class InvalidAuthError(error.UnauthorisedException):
    title = "a 401 message"


class BadRequestError(error.BadRequestException):
    title = "a 400 message"


class ServerExceptionError(error.ServerException):
    title = "a 500 message"


class ALegacyError(error.ServerException):
    code = "E500"
    title = "a 500 message"


@pytest.mark.parametrize(
    ("exc", "type_"),
    [
        (NotFoundError, "not-found"),
        (InvalidAuthError, "invalid-auth"),
        (BadRequestError, "bad-request"),
        (ServerExceptionError, "server-exception"),
    ],
)
def test_marshal(exc, type_):
    e = exc("details")

    assert e.marshal() == {
        "type": type_,
        "title": e.title,
        "details": "details",
        "status": e.status,
    }


@pytest.mark.backwards_compat()
def test_marshal_legacy():
    e = ALegacyError("debug_message")

    assert e.marshal(legacy=True) == {
        "code": "E500",
        "message": "a 500 message",
        "debug_message": "debug_message",
    }
