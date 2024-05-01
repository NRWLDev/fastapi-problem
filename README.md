# FastAPI Problems v0.7.0
[![image](https://img.shields.io/pypi/v/fastapi_problem.svg)](https://pypi.org/project/fastapi-problem/)
[![image](https://img.shields.io/pypi/l/fastapi_problem.svg)](https://pypi.org/project/fastapi-problem/)
[![image](https://img.shields.io/pypi/pyversions/fastapi_problem.svg)](https://pypi.org/project/fastapi-problem/)
![style](https://github.com/NRWLDev/fastapi-problem/actions/workflows/style.yml/badge.svg)
![tests](https://github.com/NRWLDev/fastapi-problem/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/NRWLDev/fastapi-problem/branch/main/graph/badge.svg)](https://codecov.io/gh/NRWLDev/fastapi-problem)

`fastapi_problem` is a set of exceptions and handlers for use in starlette/fastapi
applications to support easy error management and responses

Each exception easily marshals to JSON based on the
[RFC9457](https://www.rfc-editor.org/rfc/rfc9457.html) spec for use in api
errors.

## Errors

The base `fastapi_problem.error.HttpException` accepts a `title`, `details`, `status`
(default 500) and optional `**kwargs`. An additional `code` can be passed in,
which will be used as the `type`, if not provided the `type` is derived from
the class name.

And will return a JSON response with `exc.status` as the status code and response body:

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

* `fastapi_problem.error.ServerException` provides status 500 errors
* `fastapi_problem.error.BadRequestException` provides status 400 errors
* `fastapi_problem.error.UnauthorisedException` provides status 401 errors
* `fastapi_problem.error.NotFoundException` provides status 404 errors

### Custom Errors

Subclassing the convenience classes provide a simple way to consistently raise the same error
with details/extras changing based on the raised context.

```python
from fastapi_problem.error import NotFoundException


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
    import fastapi_problem.handler.starlette

    app = starlette.applications.Starlette()

    fastapi_problem.handler.starlette.add_exception_handler(app)
```

A custom logger can be provided to `add_exception_handler(app, logger=...)`.

If you require cors headers, you can pass a `fastapi_problem.cors.CorsConfiguration`
instance to `add_exception_handler(cors=...)`.

```python
add_exception_handler(
    app,
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
    from fastapi_problem.error import HttpCodeException

    class NotFoundError(HttpCodeException):
        status = 404
        message = "Endpoint not found."

    fastapi_problem.handler.starlette.add_exception_handler(
        app,
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
    import fastapi_problem.handler.fastapi


    app = fastapi.FastAPI()
    fastapi_problem.handler.fastapi.add_exception_handler(app)
```
