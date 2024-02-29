from __future__ import annotations

import typing


class HttpException(Exception):  # noqa: N818
    """
    A base exception designed to support all API error handling.
    All exceptions should inherit from this or a subclass of it (depending on the usage),
    this will allow all apps and libraries to maintain a common exception chain
    """

    def __init__(
        self: typing.Self,
        message: str,
        debug_message: str | None = None,
        code: str | None = None,
        status: int = 500,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.debug_message = debug_message

    def marshal(self: typing.Self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
            "debug_message": self.debug_message,
        }

    @classmethod
    def reraise(
        cls: HttpException,
        message: str,
        debug_message: str | None = None,
        code: str | None = None,
        status: int = 500,
    ) -> None:
        raise cls(
            message=message,
            code=code,
            debug_message=debug_message,
            status=status,
        )


class HttpCodeException(HttpException):
    status = None
    code = None
    message = None

    def __init__(self: typing.Self, debug_message: str | None = None) -> None:
        super().__init__(self.message, debug_message, self.code, self.status)


class ServerException(HttpCodeException):
    status = 500


class BadRequestException(HttpCodeException):
    status = 400


class UnauthorisedException(HttpCodeException):
    status = 401


class NotFoundException(HttpCodeException):
    status = 404
