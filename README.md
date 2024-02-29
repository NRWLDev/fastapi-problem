# Web Errors v0.6.0
[![image](https://img.shields.io/pypi/v/web_error.svg)](https://pypi.org/project/web_error/)
[![image](https://img.shields.io/pypi/l/web_error.svg)](https://pypi.org/project/web_error/)
[![image](https://img.shields.io/pypi/pyversions/web_error.svg)](https://pypi.org/project/web_error/)
![style](https://github.com/EdgyEdgemond/web-error/workflows/style/badge.svg)
![tests](https://github.com/EdgyEdgemond/web-error/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/EdgyEdgemond/web-error/branch/master/graph/badge.svg)](https://codecov.io/gh/EdgyEdgemond/web-error)

`web_error` is a set of exceptions and handlers for use in starlette/fastapi
applications to support easy error management and responses

Each exception easily marshals to JSON based on the
[[RFC9457](https://www.rfc-editor.org/rfc/rfc9457.html)] spec for use in api
errors.

## Errors

The base `web_error.error.HttpException` accepts a `title`, `details`, `status`
(default 500) and optional `**kwargs`. An additional `code` can be passed in,
which will be used as the `type`, if not provided the `type` is derived from
the class name.

And will render a json response with status as the status code:

```json
{
    "type": "an-exception",
    "title": "title",
    "details": "details",
    "status": 500,
    "extra-key": "extra-value",
    ...
}
```

Derived types are generated using the class name after dropping `...Error` from
the end, and converting to `kebab-case`. i.e. `PascalCaseError` will derive the
type `pascal-case`. If the class name doesn't suit your purposes, an optional
`code` attribute can be set with the desired value of there response `type`
field.

Some convenience Exceptions are provided with predefined `status` attributes.
To create custom errors subclasss these and define the `title` attribute.

* `web_error.error.ServerException` provides status 500 errors
* `web_error.error.BadRequestException` provides status 400 errors
* `web_error.error.UnauthorisedException` provides status 401 errors
* `web_error.error.NotFoundException` provides status 404 errors

### Custom Errors

Subclassing the convenience classes provide a simple way to consistently raise the same error
with details/extras changing based on the raised context.

```python
from web_error.error import NotFoundException


class UserNotFoundError(NotFoundException):
    title = "User not found."

raise UserNotFoundError(details="details")
```

```json
{
    "type": "user-not-found",
    "title": "User not found",
    "details": "details",
    "status": 404,
}
```

Whereas a defined `code` will be used in the output.

```python
class UserNotFoundError(NotFoundException):
    title = "User not found."
    code = "cant-find-user"

raise UserNotFoundError(details="details")
```

```json
{
    "type": "cant-find-user",
    "title": "User not found",
    "details": "details",
    "status": 404,
}
```

If additional kwargs are provided when the error is raised, they will be
included in the output (ensure the provided values are json seriablizable.


```python
raise UserNotFoundError(details="details", user_id="1234", metadata={"hello": "world"})
```

```json
{
    ...
    "details": "details",
    "user_id": "1234",
    "metadata": {"hello": "world"},
}
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
