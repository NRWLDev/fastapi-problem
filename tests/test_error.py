import pytest

from web_error import error


class A404Error(error.NotFoundException):
    code = "E404"
    message = "a 404 message"


class A401Error(error.UnauthorisedException):
    code = "E401"
    message = "a 401 message"


class A400Error(error.BadRequestException):
    code = "E400"
    message = "a 400 message"


class A500Error(error.ServerException):
    code = "E500"
    message = "a 500 message"


@pytest.mark.parametrize("exc", [
    A404Error,
    A401Error,
    A400Error,
    A500Error,
])
def test_marshal(exc):
    e = exc("debug_message")

    assert e.marshal() == {
        "code": "E{}".format(e.status),
        "message": e.message,
        "debug_message": "debug_message",
    }


@pytest.mark.parametrize("exc", [
    A404Error,
    A401Error,
    A400Error,
    A500Error,
])
def test_reraise(exc):
    e = exc("debug_message")

    d = e.marshal()

    try:
        error.HttpException.reraise(status=e.status, **d)
    except error.HttpException as exc:
        assert exc.status == e.status
        assert exc.marshal() == {
            "code": "E{}".format(e.status),
            "message": e.message,
            "debug_message": "debug_message",
        }
