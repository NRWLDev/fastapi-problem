from warnings import warn

from fastapi_problem.handler import add_exception_handler, generate_handler, request_validation_handler  # noqa: F401

warn(
    "fastapi_problem.handler.fastapi use is deprecated, use `from fastapi_problem.handler import ...` instead.",
    FutureWarning,
    stacklevel=2,
)
