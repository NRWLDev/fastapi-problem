import sys

import pytest

from fastapi_problem import util


@pytest.mark.parametrize(
    ("status_code", "title", "code"),
    [
        (500, "Internal Server Error", "http-internal-server-error"),
        (400, "Bad Request", "http-bad-request"),
        (401, "Unauthorized", "http-unauthorized"),
        (404, "Not Found", "http-not-found"),
        (409, "Conflict", "http-conflict"),
        (422, "Unprocessable Entity", "http-unprocessable-entity"),
    ],
)
@pytest.mark.skipif(sys.version_info >= (3, 13), reason="python version too new")
def test_convert_status_code_legacy(status_code, title, code):
    assert util.convert_status_code(status_code) == (title, code)


@pytest.mark.parametrize(
    ("status_code", "title", "code"),
    [
        (500, "Internal Server Error", "http-internal-server-error"),
        (400, "Bad Request", "http-bad-request"),
        (401, "Unauthorized", "http-unauthorized"),
        (404, "Not Found", "http-not-found"),
        (409, "Conflict", "http-conflict"),
        (422, "Unprocessable Content", "http-unprocessable-content"),
    ],
)
@pytest.mark.skipif(sys.version_info < (3, 13), reason="python version too old")
def test_convert_status_code(status_code, title, code):
    assert util.convert_status_code(status_code) == (title, code)
