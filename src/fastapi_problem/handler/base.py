from __future__ import annotations

import http
import typing as t

from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastapi_problem.error import Problem, StatusProblem
from fastapi_problem.handler.util import convert_status_code

if t.TYPE_CHECKING:
    import logging

    from starlette.exceptions import HTTPException

    from fastapi_problem.cors import CorsConfiguration


Handler = t.Callable[["ExceptionHandler", Request, Exception], tuple[dict, Problem]]


def http_exception_handler(eh: ExceptionHandler, _request: Request, exc: HTTPException) -> tuple[dict, Problem]:
    wrapper = eh.unhandled_wrappers.get(str(exc.status_code))
    title, code = convert_status_code(exc.status_code)
    details = exc.detail
    ret = (
        wrapper(details)
        if wrapper
        else Problem(
            title=title,
            code=code,
            details=details,
            status=exc.status_code,
        )
    )
    headers = exc.headers or {}

    return headers, ret


class ExceptionHandler:
    def __init__(  # noqa: PLR0913
        self: t.Self,
        logger: logging.Logger,
        unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
        handlers: dict[Exception, Handler] | None = None,
        *,
        strip_debug: bool = False,
        strip_debug_codes: list[int] | None = None,
    ) -> None:
        self.logger = logger
        self.unhandled_wrappers = unhandled_wrappers or {}
        self.handlers = handlers or {}
        self.strip_debug = strip_debug
        self.strip_debug_codes = strip_debug_codes or []

    def __call__(self: t.Self, request: Request, exc: Exception) -> JSONResponse:
        wrapper = self.unhandled_wrappers.get("default", self.unhandled_wrappers.get("500"))
        ret = (
            wrapper(str(exc))
            if wrapper
            else Problem(
                title="Unhandled exception occurred.",
                details=str(exc),
                code="unhandled-exception",
            )
        )
        headers = {}

        for exc_type, handler in self.handlers.items():
            if isinstance(exc, exc_type):
                headers_, ret = handler(self, request, exc)
                headers.update(headers_)
                break

        if isinstance(exc, Problem):
            ret = exc

        if ret.status >= http.HTTPStatus.INTERNAL_SERVER_ERROR:
            self.logger.exception(ret.title, exc_info=(type(exc), exc, exc.__traceback__))

        strip_debug_ = self.strip_debug or ret.status in self.strip_debug_codes

        if strip_debug_ and (ret.details or ret.extras):
            msg = "Stripping debug information from exception."
            self.logger.debug(msg)

            for k, v in {
                "details": ret.details,
                **ret.extras,
            }.items():
                msg = f"Removed {k}: {v}"
                self.logger.debug(msg)

        headers["content-type"] = "application/problem+json"

        return JSONResponse(
            status_code=ret.status,
            content=ret.marshal(strip_debug=strip_debug_),
            headers=headers,
        )


def cors_wrapper_factory(
    cors: CorsConfiguration,
    handler: t.Callable[[Request, Exception], JSONResponse],
) -> t.Callable[[Request, Exception], JSONResponse]:
    def wrapper(request: Request, exc: Exception) -> JSONResponse:
        response = handler(request, exc)

        # Since the CORSMiddleware is not executed when an unhandled server exception
        # occurs, we need to manually set the CORS headers ourselves if we want the FE
        # to receive a proper JSON 500, opposed to a CORS error.
        # Setting CORS headers on server errors is a bit of a philosophical topic of
        # discussion in many frameworks, and it is currently not handled in FastAPI.
        # See dotnet core for a recent discussion, where ultimately it was
        # decided to return CORS headers on server failures:
        # https://github.com/dotnet/aspnetcore/issues/2378
        origin = request.headers.get("origin")

        if origin:
            # Have the middleware do the heavy lifting for us to parse
            # all the config, then update our response headers
            mw = CORSMiddleware(
                app=None,
                allow_origins=cors.allow_origins,
                allow_credentials=cors.allow_credentials,
                allow_methods=cors.allow_methods,
                allow_headers=cors.allow_headers,
            )

            # Logic directly from Starlette"s CORSMiddleware:
            # https://github.com/encode/starlette/blob/master/starlette/middleware/cors.py#L152

            response.headers.update(mw.simple_headers)
            has_cookie = "cookie" in request.headers

            # If request includes any cookie headers, then we must respond
            # with the specific origin instead of "*".
            if mw.allow_all_origins and has_cookie:
                response.headers["Access-Control-Allow-Origin"] = origin

            # If we only allow specific origins, then we have to mirror back
            # the Origin header in the response.
            elif not mw.allow_all_origins and mw.is_allowed_origin(origin=origin):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers.add_vary_header("Origin")

        return response

    return wrapper
