# Usage

```python
import fastapi
import fastapi_problem.handler


app = fastapi.FastAPI()
eh = fastapi_problem.handler.new_exception_handler()
fastapi_problem.handler.add_exception_handler(app, eh)
```

A custom logger can be provided using:

```python
new_exception_handler(
    logger=...,
)
```

If you require cors headers, you can pass a `fastapi_problem.cors.CorsConfiguration`
instance to `new_exception_handler(cors=...)`.

```python
new_exception_handler(
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
from fastapi_problem.handler import add_exception_handler, new_exception_handler

class NotFoundError(StatusProblem):
    status = 404
    message = "Endpoint not found."

eh = new_exception_handler(
    unhandled_wrappers={
        "404": NotFoundError,
    },
)
add_exception_handler(app, eh)
```

If you wish to hide debug messaging from external users, `StripExtrasPostHook`
allows modifying the response content. `mandatory_fields` supports defining
fields that should always be returned, default fields are `["type", "title",
"status", "detail"]`.

For more fine-grained control, `exclude_status_codes=[500, ...]` can be used to
allow extras for specific status codes. Allowing expected fields to reach the
user, while suppressing unexpected server errors etc.

```python
from fastapi_problem.handler import StripExtrasPostHook, add_exception_handler, new_exception_handler

eh = new_exception_handler(
    post_hooks=[
        StripExtrasPostHook(
            mandatory_fields=["type", "title", "status", "detail", "custom-extra"],
            exclude_status_codes=[400],
            enabled=True,
        )
    ],
)
add_exception_handler(app, eh)
```

## Swagger

When the exception handlers are registered, the default `422` response type is
updated to match the Problem format instead of the FastAPI default response.

A generic `4XX` and `5XX` response is added to each path as well, these can be
opted out of by passing `generic_swagger_defaults=False` when registering the
exception handlers.

```python
eh = new_exception_handler(
    generic_swagger_defaults=False,
)
add_exception_handler(app, eh)
```

To specify specific error responses per endpoint, when registering the route
the swagger responses for each possible error can be generated using the
`generate_swagger_response` helper method. Multiple exceptions can be provided
if the route can return different errors of the same status code.

```
from fastapi_problem.error import StatusProblem
from fastapi_problem.handler import generate_swagger_response

class NotFoundError(StatusProblem):
    status = 404
    title = "Endpoint not found."


eh = new_exception_handler()
add_exception_handler(app, eh)

@app.post(
    "/path",
    responses={400: eh.generate_swagger_response(NotFoundError)}},
)
...
```
## Sentry

`fastapi_problem` is designed to play nicely with [Sentry](https://sentry.io),
there is no need to do anything special to integrate with sentry other than
initializing the sdk. The Starlette and Fastapi integrations paired with the
Logging integration will take care of everything.

To prevent duplicated entries, ignoing the `uvicorn.error` logger in sentry can
be handy.
