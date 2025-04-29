# Custom Handler

In the event that you are using a third party library with a custom error
class, a handler specifically a common base class can be provided.

Providing a custom handler allows for conversion from the custom error class
into a `Problem`, when the exception handler catches it, rather than converting
each raised instance into a `Problem` at the time it is raised.

## Usage

Given a `third_party` library with a `error.py` module.

```python
class CustomBaseError(Exception):
    def __init__(reason: str, debug: str):
        self.reason = reason
        self.debug = debug
```

A custom handler can then be defined in your application.

```python
import fastapi
from rfc9457 import error_class_to_type
from fastapi_problem.error import Problem
from fastapi_problem.handler import ExceptionHandler, add_exception_handler, new_exception_handler
from starlette.requests import Request

from third_party.error import CustomBaseError

def my_custom_handler(eh: ExceptionHandler, request: Request, exc: CustomBaseError) -> Problem:
    return Problem(
        title=exc.reason,
        detail=exc.debug,
        type_=error_class_to_type(exc),
        status=500,
        headers={"x-custom-header": "value"},
    )

app = fastapi.FastAPI()
eh = new_exception_handler(
    handlers={
        CustomBaseError: my_custom_handler,
    },
)
add_exception_handler(app, eh)
```

Any instance of CustomBaseError, or any subclasses, that reach the exception
handler will then be converted into a Problem response, as opposed to an
unhandled error response.

## Builtin Handlers

Starlette HTTPException and fastapi RequestValidationError instances are
handled by default, to customise how these errors are processed, provide a
handler for `starlette.exceptions.HTTPException` or
`fastapi.exceptions.RequestValidationError`, similar to the custom handlers
previously defined, but rather than passing it to handlers, use the
`http_exception_handler` and `request_validation_handler` parameters respectively.

```python
import fastapi
from fastapi_problem.error import Problem
from fastapi_problem.handler import ExceptionHandler, add_exception_handler, new_exception_handler
from starlette.exceptions import HTTPException
from starlette.requests import Request


def my_custom_handler(eh: ExceptionHandler, request: Request, exc: HTTPException) -> Problem:
    return Problem(...)


app = fastapi.FastAPI()
eh = new_excep, new_exception_handler(
    http_exception_handler=my_custom_handler,
)
add_exception_handler(app, eh)
```

### Optional handling

In some cases you may want to handle specific cases for a type of exception,
but let others defer to another handler. In these scenarios, a custom handler
can return None rather than a Problem. If a handler returns None the exception
will be pass to the next defined handler.

```python
import fastapi
from rfc9457 import error_class_to_type
from fastapi_problem.error import Problem
from fastapi_problem.handler import ExceptionHandler, add_exception_handler, new_exception_handler
from starlette.requests import Request

def no_response_handler(eh: ExceptionHandler, request: Request, exc: RuntimeError) -> Problem | None:
    if str(exc) == "No response returned.":
        return Problem(
            title="No response returned.",
            detail="starlette bug",
            type_="no-response",
            status=409,
        )
    return None

def base_handler(eh: ExceptionHandler, request: Request, exc: Exception) -> Problem:
    return Problem(
        title=exc.reason,
        detail=exc.debug,
        type_=error_class_to_type(exc),
        status=500,
    )

app = fastapi.FastAPI()
eh = new_exception_handler(
    handlers={
        RuntimeError: no_response_handler,
        Exception: base_handler,
    },
)
add_exception_handler(app, eh)
```

At the time of writing there was (is?) a
[bug](https://github.com/encode/starlette/issues/2516) in starlette that would
cause middlewares to error.  To prevent these from reaching Sentry, a deferred
handler was implemented in the impacted project.
