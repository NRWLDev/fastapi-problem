# Usage

```python
import fastapi
import fastapi_problem.handler.fastapi


app = fastapi.FastAPI()
fastapi_problem.handler.fastapi.add_exception_handler(app)
```

A custom logger can be provided using:

```python
add_exception_handler(
    app,
    logger=...,
)
```

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

```python
from fastapi_problem.error import HttpCodeException
from fastapi_problem.handler.fastapi import add_exception_handler

class NotFoundError(HttpCodeException):
    status = 404
    message = "Endpoint not found."

add_exception_handler(
    app,
    unhandled_wrappers={
        "404": NotFoundError,
    },
)
```

If you wish to hide debug messaging from external users, `strip_debug=True`
will log the details and remove it from the response.

For more fine-grained control, `strip_debug_codes=[500, ...]` can be used to
strip debug messaging from specific status codes. Allowing expected debug
messages to reach the user, while suppressing unexpected server errors etc.

```python
from fastapi_problem.handler.fastapi import add_exception_handler

add_exception_handler(
    app,
    strip_debug_dodes=[500],
)
```

## Starlette

As FastAPI is written on top of starlette, an additional handler is available
which does not handle FastAPI's RequestValidationErrors. All configuration is
the same as above.

```python
import starlette.applications
from fastapi_problem.handler.starlette add_exception_handler

app = starlette.applications.Starlette()

add_exception_handler(app)
```
