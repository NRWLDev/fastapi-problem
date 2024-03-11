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
    message = "a 500 message"


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
def test_legacy_attributes_new_error():
    e = NotFoundError("details")

    assert e.message == e.title
    assert e.code is None
    assert e.debug_message == e.details


@pytest.mark.backwards_compat()
def test_legacy_attributes():
    e = ALegacyError("details")

    assert e.message == e.title
    assert e.code == e.type
    assert e.debug_message == e.details


@pytest.mark.backwards_compat()
def test_marshal_legacy():
    e = ALegacyError("debug_message")

    assert e.marshal(legacy=True) == {
        "code": "E500",
        "message": "a 500 message",
        "debug_message": "debug_message",
    }


@pytest.mark.backwards_compat()
def test_init_legacy():
    e = error.HttpException(
        message="Unable to connect to service.",
        debug_message="debug_message",
        code="E000",
        status=400,
    )

    assert e.marshal() == {
        "type": "E000",
        "title": "Unable to connect to service.",
        "details": "debug_message",
        "status": 400,
    }


@pytest.mark.backwards_compat()
def test_init_legacy_no_message():
    with pytest.raises(TypeError) as e:
        error.HttpException(
            debug_message="debug_message",
            code="E000",
            status=400,
        )

    assert str(e.value) == "HttpException.__init__() missing 1 required positional argument: 'title'"
