"""Implement RFC9547 compatible exceptions.

https://www.rfc-editor.org/rfc/rfc9457.html
"""

from __future__ import annotations

import re
import typing as t

CONVERT_RE = re.compile(r"(?<!^)(?=[A-Z])")


class HttpException(Exception):  # noqa: N818
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
        self.warn = True

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


class HttpCodeException(HttpException):
    code = None
    title = "Base http exception."
    status = 500

    def __init__(self: t.Self, details: str | None = None, **kwargs) -> None:
        self.warn = False
        super().__init__(self.title, code=self.code, details=details, status=self.status, **kwargs)


class ServerException(HttpCodeException): ...


class BadRequestException(HttpCodeException):
    status = 400


class UnauthorisedException(HttpCodeException):
    status = 401


class NotFoundException(HttpCodeException):
    status = 404
