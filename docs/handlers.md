# Custom Handler

In the event that you have custom error classes, a handler specifically a
common base class can be provided, allowing for conversion from the custom
error class into a `Problem`. Custom handlers can also inject headers into the
response.

```python
import fastapi
from fastapi_problem.error import Problem
from fastapi_problem.handler.base import ExceptionHandler
from fastapi_problem.handler.fastapi import add_exception_handler
from starlette.requests import Request

from my_module.error import CustomBaseError

def my_custom_handler(eh: ExceptionHandler, request: Request, exc: CustomBaseError) -> tuple[dict, Problem]:
    p = Problem(
        title=str(exc),
        details=exc.debug,
        code=500,
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
