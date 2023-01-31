import logging

from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from web_error.error import HttpException


logger = logging.getLogger(__name__)


def exception_handler(request: Request, exc: Exception):
    status = 500
    message = "Unhandled exception occurred."
    response = {
        "message": message,
        "debug_message": str(exc),
        "code": None,
    }

    if isinstance(exc, HTTPException):
        response["message"] = exc.detail
        status = exc.status_code

    if isinstance(exc, HttpException):
        response = exc.marshal()
        status = exc.status

    if status >= 500:
        logger.exception(message, exc_info=(type(exc), exc, exc.__traceback__))

    return JSONResponse(
        status_code=status,
        content=response,
    )


def generate_handler_with_cors(
    allow_origins=None,
    allow_credentials=True,
    allow_methods=None,
    allow_headers=None,
    _exception_handler=exception_handler,  # allow fastapi to pass in exception handler
):
    allow_origins = allow_origins if allow_origins is not None else ["*"]
    allow_methods = allow_methods if allow_methods is not None else ["*"]
    allow_headers = allow_headers if allow_headers is not None else ["*"]

    def inner(request: Request, exc: Exception):
        response = _exception_handler(request, exc)

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
            cors = CORSMiddleware(
                app=None,
                allow_origins=allow_origins,
                allow_credentials=allow_credentials,
                allow_methods=allow_methods,
                allow_headers=allow_headers,
            )

            # Logic directly from Starlette"s CORSMiddleware:
            # https://github.com/encode/starlette/blob/master/starlette/middleware/cors.py#L152

            response.headers.update(cors.simple_headers)
            has_cookie = "cookie" in request.headers

            # If request includes any cookie headers, then we must respond
            # with the specific origin instead of "*".
            if cors.allow_all_origins and has_cookie:
                response.headers["Access-Control-Allow-Origin"] = origin

            # If we only allow specific origins, then we have to mirror back
            # the Origin header in the response.
            elif not cors.allow_all_origins and cors.is_allowed_origin(origin=origin):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers.add_vary_header("Origin")

        return response
    return inner
