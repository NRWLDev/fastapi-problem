"""
Run this example:
$ fastapi dev examples/custom.py

To see a custom 422, fastapi RequestValidationError response.
$ curl http://localhost:8000/validation-error

To see a custom unhandled server error response.
$ curl http://localhost:8000/unexpected-error

To see a custom starlette 405 error response.
$ curl http://localhost:8000/not-allowed

To see a custom starlette 404 error response.
$ curl http://localhost:8000/not-found
"""

import logging

import fastapi

from fastapi_problem.handler import add_exception_handler, new_exception_handler
from fastapi_problem.error import NotFoundProblem, ServerProblem, StatusProblem, UnprocessableProblem

logging.getLogger("uvicorn.error").disabled = True


class CustomNotFound(NotFoundProblem):
    title = "Endpoint not available."


class CustomNotAllowed(StatusProblem):
    title = "Method not available."
    status = 405


class CustomValidation(UnprocessableProblem):
    title = "Validation failed."


class CustomServer(ServerProblem):
    title = "Server failed."


app = fastapi.FastAPI()

eh = new_exception_handler(
    unhandled_wrappers={
        "404": CustomNotFound,
        "405": CustomNotAllowed,
        "422": CustomValidation,
        "default": CustomServer,
    },
)
add_exception_handler(app, eh)


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
