"""Implement RFC9547 compatible exceptions.

https://www.rfc-editor.org/rfc/rfc9457.html
"""

from __future__ import annotations

import typing as t
from warnings import warn

from rfc9457 import (
    BadRequestProblem,
    ConflictProblem,
    ForbiddenProblem,
    NotFoundProblem,
    Problem,
    ServerProblem,
    StatusProblem,
    UnauthorisedProblem,
    UnprocessableProblem,
)


class HttpException(Problem):
    def __init__(
        self: t.Self,
        title: str,
        type_: str | None = None,
        details: str | None = None,
        status: int = 500,
        **kwargs,
    ) -> None:
        warn(
            "HttpException use is deprecated, use `Problem` subclasses instead.",
            FutureWarning,
            stacklevel=2,
        )
        super().__init__(title, type_=type_, details=details, status=status, **kwargs)


class HttpCodeException(StatusProblem):
    def __init__(self: t.Self, details: str | None = None, **kwargs) -> None:
        warn(
            "HttpCodeException use is deprecated, use `StatusProblem` subclasses instead.",
            FutureWarning,
            stacklevel=2,
        )
        super().__init__(details=details, **kwargs)


class ServerException(HttpCodeException): ...


class BadRequestException(HttpCodeException):
    status = 400


class UnauthorisedException(HttpCodeException):
    status = 401


class NotFoundException(HttpCodeException):
    status = 404


__all__ = [
    "Problem",
    "StatusProblem",
    "BadRequestProblem",
    "NotFoundProblem",
    "ServerProblem",
    "UnauthorisedProblem",
    "ForbiddenProblem",
    "ConflictProblem",
    "UnprocessableProblem",
    "HttpException",
    "ServerException",
    "BadRequestException",
    "UnauthorisedException",
    "NotFoundException",
]
