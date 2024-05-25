from warnings import warn

from fastapi_problem.util import convert_status_code  # noqa: F401

warn(
    "fastapi_problem.handler.util use is deprecated, use `from fastapi_problem.handler import ...` instead.",
    FutureWarning,
    stacklevel=2,
)
