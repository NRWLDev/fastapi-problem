# Hooks

Custom pre/post hook functions can be provided to the exception handler.

## Pre Hooks

A pre hook will be provided with the current request, and exception. There
should be no side effects in pre hooks and no return value, they can be used
for informational purposes such as logging or debugging.

```python
import logging

import fastapi
from fastapi_problem.handler import add_exception_handler
from starlette.requests import Request

logger = logging.getLogger(__name__)


def custom_hook(request: Request, exc: Exception) -> None:
    logger.debug(type(exc))
    logger.debug(request.headers)


app = fastapi.FastAPI()
add_exception_handler(
    app,
    pre_hooks=[custom_hook],
)
```

## Post Hooks

A post hook will be provided with the raw content object, the incoming request,
and the current response object. Post hooks can mutate the response object to
provide additional headers etc. The CORS header implementation is done using a
post hook. In the case the response format should be changed (if you have an
xml api etc, the raw content can be reprocessed.).

```python
import fastapi
from fastapi_problem.handler import add_exception_handler
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


def custom_hook(content: dict, request: Request, response: Response) -> Response:
    if "x-custom-header" in request.headers:
        response.headers["x-custom-response"] = "set"

    return content, response


app = fastapi.FastAPI()
add_exception_handler(
    app,
    post_hooks=[custom_hook],
)
```
