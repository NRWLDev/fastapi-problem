"""Implement RFC9547 compatible exceptions.

https://www.rfc-editor.org/rfc/rfc9457.html
"""

from __future__ import annotations

import re
import typing as t
from warnings import warn

CONVERT_RE = re.compile(r"(?<!^)(?=[A-Z])")


class Problem(Exception):  # noqa: N818
    """
    A base exception designed to support all API error handling.
    All exceptions should inherit from this or a subclass of it (depending on the usage),
    this will allow all apps and libraries to maintain a common exception chain
    """

    def __init__(
        self: t.Self,
        title: str,
        code: str | None = None,
        details: str | None = None,
        status: int = 500,
        **kwargs,
    ) -> None:
        super().__init__(title)
        self._code = code
        self.title = title
        self.details = details
        self.status = status
        self.extras = kwargs

    @property
    def type(self: t.Self) -> str:
        type_ = "".join(self.__class__.__name__.rsplit("Error", 1))
        type_ = CONVERT_RE.sub("-", type_).lower()
        return self._code if self._code else type_

    def marshal(self: t.Self, *, strip_debug: bool = False) -> dict[str, t.Any]:
        """Generate a JSON compatible representation.

        Args:
        ----
            strip_debug: If true, remove anything that is not title/type.
        """
        ret = {
            "type": self.type,
            "title": self.title,
            "status": self.status,
        }

        if self.details:
            ret["details"] = self.details

        for k, v in self.extras.items():
            ret[k] = v

        if strip_debug:
            ret = {k: v for k, v in ret.items() if k in ["type", "title", "status"]}

        return ret


class HttpException(Problem):
    def __init__(
        self: t.Self,
        title: str,
        code: str | None = None,
        details: str | None = None,
        status: int = 500,
        **kwargs,
    ) -> None:
        warn(
            "HttpException use is deprecated, use `Problem` subclasses instead.",
            FutureWarning,
            stacklevel=2,
        )
        super().__init__(title, code=code, details=details, status=status, **kwargs)


class StatusProblem(Problem):
    code = None
    title = "Base http exception."
    status = 500

    def __init__(self: t.Self, details: str | None = None, **kwargs) -> None:
        super().__init__(self.title, code=self.code, details=details, status=self.status, **kwargs)


class HttpCodeException(StatusProblem):
    def __init__(self: t.Self, details: str | None = None, **kwargs) -> None:
        warn(
            "HttpCodeException use is deprecated, use `StatusProblem` subclasses instead.",
            FutureWarning,
            stacklevel=2,
        )
        super().__init__(details=details, **kwargs)


class ServerProblem(StatusProblem): ...


class ServerException(HttpCodeException): ...


class BadRequestProblem(StatusProblem):
    status = 400


class BadRequestException(HttpCodeException):
    status = 400


class UnauthorisedProblem(StatusProblem):
    status = 401


class UnauthorisedException(HttpCodeException):
    status = 401


class ForbiddenProblem(StatusProblem):
    status = 403


class NotFoundProblem(StatusProblem):
    status = 404


class NotFoundException(HttpCodeException):
    status = 404


class ConflictProblem(StatusProblem):
    status = 409
