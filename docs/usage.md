# Usage

```python
import fastapi
import fastapi_problem.handler


app = fastapi.FastAPI()
fastapi_problem.handler.add_exception_handler(app)
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

To customise the way that errors, that are not a subclass of Problem, are
handled provide `unhandled_wrappers`, a dict mapping an http status code to
a `StatusProblem`, the system key `default` is also accepted as the root wrapper
for all unhandled exceptions.

```python
from fastapi_problem.error import StatusProblem
from fastapi_problem.handler import add_exception_handler

class NotFoundError(StatusProblem):
    status = 404
    message = "Endpoint not found."

add_exception_handler(
    app,
    unhandled_wrappers={
        "404": NotFoundError,
    },
)
```

If you wish to hide debug messaging from external users, `StripExtrasPostHook`
allows modifying the response content. `mandatory_fields` supports defining
fields that should always be returned, default fields are `["type", "title",
"status", "detail"]`.

For more fine-grained control, `exclude_status_codes=[500, ...]` can be used to
allow extras for specific status codes. Allowing expected fields to reach the
user, while suppressing unexpected server errors etc.

```python
from fastapi_problem.handler import StripExtrasPostHook, add_exception_handler

add_exception_handler(
    app,
    post_hooks=[
        StripExtrasPostHook(
            mandatory_fields=["type", "title", "status", "detail", "custom-extra"],
            exclude_status_codes=[400],
            enabled=True,
        )
    ],
)
```

## Sentry

`fastapi_problem` is designed to play nicely with [Sentry](https://sentry.io),
there is no need to do anything special to integrate with sentry other than
initializing the sdk. The Starlette and Fastapi integrations paired with the
Logging integration will take care of everything.

To prevent duplicated entries, ignoing the `uvicorn.error` logger in sentry can
be handy.
