"""
Run this example:
$ fastapi dev examples/builtin.py

To see a standard 422, fastapi RequestValidationError response.
$ curl http://localhost:8000/validation-error

To see a standard unhandled server error response.
$ curl http://localhost:8000/unexpected-error

To see a standard starlette 405 error response.
$ curl http://localhost:8000/not-allowed

To see a standard starlette 404 error response.
$ curl http://localhost:8000/not-found
"""

import fastapi

from fastapi_problem.handler.fastapi import add_exception_handler

app = fastapi.FastAPI()

add_exception_handler(
    app,
)


@app.get("/validation-error")
async def validation_error(required: str) -> dict:
    return {}


@app.post("/not-allowed")
async def method_not_allowed() -> dict:
    return {}


@app.get("/unexpected-error")
async def unexpected_error() -> dict:
    return {"value": 1 / 0}


if __name__ == "__main__":
    app.run()
