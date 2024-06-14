"""Implement RFC9547 compatible exceptions.

https://www.rfc-editor.org/rfc/rfc9457.html
"""

from rfc9457 import (
    BadRequestProblem,
    ConflictProblem,
    ForbiddenProblem,
    NotFoundProblem,
    Problem,
    RedirectProblem,
    ServerProblem,
    StatusProblem,
    UnauthorisedProblem,
    UnprocessableProblem,
)

__all__ = [
    "Problem",
    "StatusProblem",
    "BadRequestProblem",
    "ConflictProblem",
    "ForbiddenProblem",
    "NotFoundProblem",
    "RedirectProblem",
    "ServerProblem",
    "UnauthorisedProblem",
    "UnprocessableProblem",
]
