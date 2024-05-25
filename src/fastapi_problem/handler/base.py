from warnings import warn

from fastapi_problem.handler import (  # noqa: F401
    CorsPostHook,
    ExceptionHandler,
    Handler,
    PostHook,
    PreHook,
    http_exception_handler,
)

warn(
    "fastapi_problem.handler.base use is deprecated, use `from fastapi_problem.handler import ...` instead.",
    FutureWarning,
    stacklevel=2,
)
