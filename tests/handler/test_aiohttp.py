import json
from unittest import mock

import pytest
from aiohttp import web_exceptions

from web_error import error
from web_error.handler import aiohttp


@aiohttp.view_error_handler
async def view_test(exception):
    raise exception


class ATestError(error.BadRequestException):
    message = "This is an error."
    code = "E123"


class TestExceptionHandler:
    @pytest.mark.asyncio
    async def test_unexpected_error(self, monkeypatch):
        monkeypatch.setattr(aiohttp.logger, "exception", mock.Mock())

        exc = Exception("Something went bad")

        response = await view_test(exc)

        assert response.status == 500
        assert json.loads(response.text) == {
            "message": "Unhandled exception occurred.", "debug_message": "Something went bad", "code": None,
        }
        assert aiohttp.logger.exception.call_args == mock.call("Unhandled exception occurred.")

    @pytest.mark.asyncio
    async def test_aiohttp_error(self):
        exc = web_exceptions.HTTPNotFound()

        response = await view_test(exc)

        assert response.status == 404
        assert json.loads(response.text) == {
            "message": "HTTPNotFound", "debug_message": "404: Not Found", "code": None,
        }

    @pytest.mark.asyncio
    async def test_known_error(self):
        exc = ATestError("something bad")

        response = await view_test(exc)

        assert response.status == 400
        assert json.loads(response.text) == {
            "message": "This is an error.", "debug_message": "something bad", "code": "E123",
        }
