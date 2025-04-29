"""
Run this example:
$ fastapi dev examples/builtin.py

To see a standard 422, fastapi RequestValidationError response.
$ curl http://localhost:8000/validation-error

To see a standard 422, fastapi RequestValidationError form validation response.
$ curl http://localhost:8000/validation-error -X POST -H "Content-Type: application/json" --data '{"other": [{"inner_required": "provided"}, {}]}'

To see a standard unhandled server error response.
$ curl http://localhost:8000/unexpected-error

To see a standard starlette 405 error response.
$ curl http://localhost:8000/not-allowed

To see a standard starlette 404 error response.
$ curl http://localhost:8000/not-found
"""

import logging

import fastapi
import pydantic

from fastapi_problem.handler import add_exception_handler, new_exception_handler

logging.getLogger("uvicorn.error").disabled = True

app = fastapi.FastAPI()

eh = new_exception_handler()
add_exception_handler(app, eh)


@app.get("/validation-error")
async def validation_error(required: str) -> dict:
    return {}


class Other(pydantic.BaseModel):
    inner_required: str


class NestedBody(pydantic.BaseModel):
    required: str
    other: list[Other]


@app.post("/validation-error")
async def validation_error(
    data: NestedBody,
) -> dict:
    return {}


@app.post("/not-allowed")
async def method_not_allowed() -> dict:
    return {}


@app.get("/unexpected-error")
async def unexpected_error() -> dict:
    return {"value": 1 / 0}


if __name__ == "__main__":
    app.run()
