# Web Errors v0.5.6
[![image](https://img.shields.io/pypi/v/web_error.svg)](https://pypi.org/project/web_error/)
[![image](https://img.shields.io/pypi/l/web_error.svg)](https://pypi.org/project/web_error/)
[![image](https://img.shields.io/pypi/pyversions/web_error.svg)](https://pypi.org/project/web_error/)
![style](https://github.com/EdgyEdgemond/web-error/workflows/style/badge.svg)
![tests](https://github.com/EdgyEdgemond/web-error/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/EdgyEdgemond/web-error/branch/master/graph/badge.svg)](https://codecov.io/gh/EdgyEdgemond/web-error)

`web_error` is a set of exceptions and handlers for use in web apis to support easy error management and responses

Each exception easily marshals to JSON for use in api errors. Handlers for different web frameworks are provided.


## Errors

The base `web_error.error.HttpException` accepts a `message`, `debug_message`, `code` and `status` (default 500)

And will render a response with status as the status code:

```json
{
    "code": "code",
    "message": "message",
    "debug_message": "debug_message",
}
```

Some convenience Exceptions are provided, to create custom error subclass these
and define `message` and `code` attributes.

* `web_error.error.ServerException` provides status 500 errors
* `web_error.error.BadRequestException` provides status 400 errors
* `web_error.error.UnauthorisedException` provides status 401 errors
* `web_error.error.NotFoundException` provides status 404 errors

### Custom Errors

Subclassing the convenience classes provide a simple way to consistently raise the same error
and message.

Code is an optional attribute to provide a unique value to parse in a frontend/client instead of
matching against messages.

```python
from web_error.error import NotFoundException


class UserNotFoundError(NotFoundException):
    message = "User not found."
    code = "E001"
```

## Starlette


```python
    import starlette.applications
    import web_error.handler.starlette

    exception_handler = web_error.handler.starlette.generate_handler()

    return starlette.applications.Starlette(
        exception_handlers={
            Exception: exception_handler,
            HTTPException: exception_handler,
        },
    )
```

A custom logger can be provided to `generate_handler(logger=...)`.

If you require cors headers, you can pass a `web_error.cors.CorsConfiguration`
instance to `generate_handler(cors=...)`.

```python
generate_handler(
    cors=CorsConfiguration(
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
)
```

To handle unexpected errors provide `unhandled_wrappers`, a dict mapping http
status code to `HttpCodeException`, the system key `default` is also accepted
as the root wrapper for all unhandled exceptions.

If you wish to hide debug messaging from external users, `strip_debug=True`
will log the debug message and remove it from the response.

```python
    from web_error.error import HttpCodeException

    class NotFoundError(HttpCodeException):
        status = 404
        message = "Endpoint not found."

    exception_handler = web_error.handler.starlette.generate_handler(
        unhandled_wrappers={
            "404": NotFoundError,
        },
    )
```

## FastAPI

The FastAPI handler is identical to the starlette handler with the additional
handling of `RequestValidationError`.

```python
    import fastapi
    import web_error.handler.fastapi

    exception_handler = web_error.handler.fastapi.generate_handler()

    return fastapi.FastAPI(
        exception_handlers={
            Exception: exception_handler,
            RequestValidationError: exception_handler,
            HTTPException: exception_handler,
        },
    )
```
