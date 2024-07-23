# FastAPI Problems
[![image](https://img.shields.io/pypi/v/fastapi_problem.svg)](https://pypi.org/project/fastapi-problem/)
[![image](https://img.shields.io/pypi/l/fastapi_problem.svg)](https://pypi.org/project/fastapi-problem/)
[![image](https://img.shields.io/pypi/pyversions/fastapi_problem.svg)](https://pypi.org/project/fastapi-problem/)
![style](https://github.com/NRWLDev/fastapi-problem/actions/workflows/style.yml/badge.svg)
![tests](https://github.com/NRWLDev/fastapi-problem/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/NRWLDev/fastapi-problem/branch/main/graph/badge.svg)](https://codecov.io/gh/NRWLDev/fastapi-problem)

`fastapi_problem` is a set of exceptions and handlers for use in fastapi
applications to support easy error management and responses.

Each exception easily marshals to JSON based on the
[RFC9457](https://www.rfc-editor.org/rfc/rfc9457.html) spec for use in api
errors.

Check the [docs](https://nrwldev.github.io/fastapi-problem) for more details.

## Custom Errors

Subclassing the convenience classes provide a simple way to consistently raise
the same error with detail/extras changing based on the raised context.

```python
from fastapi_problem.error import NotFoundProblem


class UserNotFoundError(NotFoundProblem):
    title = "User not found."

raise UserNotFoundError(detail="detail")
```

```json
{
    "type": "user-not-found",
    "title": "User not found",
    "detail": "detail",
    "status": 404,
}
```

## Usage

```python
import fastapi
from fastapi_problem.handler import add_exception_handler


app = fastapi.FastAPI()
add_exception_handler(app)

@app.get("/user")
async def get_user():
    raise UserNotFoundError("No user found.")
```

```bash
$ curl localhost:8000/user
{

    "type": "user-not-found",
    "title": "User not found",
    "detail": "No user found.",
    "status": 404,
}
```
