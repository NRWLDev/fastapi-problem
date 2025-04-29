"""
Run this example:
$ fastapi dev examples/override.py

To see a custom starlette 405 error response.
$ curl http://localhost:8000/not-allowed

To see a custom starlette 404 error response.
$ curl http://localhost:8000/not-found
"""

import logging

import fastapi
from starlette.exceptions import HTTPException

from fastapi_problem.handler import ExceptionHandler, add_exception_handler, new_exception_handler
from fastapi_problem.error import NotFoundProblem, Problem, ServerProblem, StatusProblem

logging.getLogger("uvicorn.error").disabled = True


class CustomNotFoundProblem(NotFoundProblem):
    type_ = "not-found"
    title = "Endpoint not available."


class CustomNotAllowedProblem(StatusProblem):
    status = 405
    type_ = "method-not-allowed"
    title = "Method not allowed."


status_mapping = {
    "404": (CustomNotFoundProblem, "The requested endpoint does not exist."),
    "405": (CustomNotAllowedProblem, "This method is not allowed."),
}


def http_exception_handler(
    _eh: ExceptionHandler,
    _request: fastapi.Request,
    exc: HTTPException,
) -> Problem:
    exc, detail = status_mapping.get(str(exc.status_code))
    return exc(detail)


app = fastapi.FastAPI()

eh = new_exception_handler(
    http_exception_handler=http_exception_handler,
)
add_exception_handler(app, eh)


@app.post("/not-allowed")
async def method_not_allowed() -> dict:
    return {}


if __name__ == "__main__":
    app.run()
