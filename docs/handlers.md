# Custom Handler

In the event that you are using a third party library with a custom error
class, a handler specifically a common base class can be provided.

Providing a custom handler allows for conversion from the custom error class
into a `Problem`, when the exception handler catches it, rather than converting
each raised instance into a `Problem` at the time it is raised.

Custom handlers can also inject headers into the response.

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
from fastapi_problem.handler.base import ExceptionHandler
from fastapi_problem.handler.fastapi import add_exception_handler
from starlette.requests import Request

from third_party.error import CustomBaseError

def my_custom_handler(eh: ExceptionHandler, request: Request, exc: CustomBaseError) -> tuple[dict, Problem]:
    p = Problem(
        title=exc.reason,
        details=exc.debug,
        type_=error_class_to_type(exc),
        status=500,
    )

    return {"x-custom-header": "value"}, p

app = fastapi.FastAPI()
add_exception_handler(
    app,
    handlers={
        CustomBaseError: my_custom_handler,
    },
)
```

Any instance of CustomBaseError, or any subclasses, that reach the exception
handler will then be converted into a Problem response, as opposed to an
unhandled error response.
