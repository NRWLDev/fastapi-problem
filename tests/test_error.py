import pytest

from fastapi_problem import error


class NotFoundError(error.NotFoundProblem):
    title = "a 404 message"


class InvalidAuthError(error.UnauthorisedProblem):
    title = "a 401 message"


class BadRequestError(error.BadRequestProblem):
    title = "a 400 message"


class ServerExceptionError(error.ServerProblem):
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


def test_subclass_chain():
    assert isinstance(NotFoundError("details"), error.Problem)
    assert isinstance(NotFoundError("details"), error.StatusProblem)
