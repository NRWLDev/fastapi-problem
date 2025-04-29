"""
Run this example:
$ fastapi dev examples/basic.py

To see a standard expected user error response.
$ curl http://localhost:8000/user-error

To see a standard expected server error response.
$ curl http://localhost:8000/user-error
"""

import logging

import fastapi

from fastapi_problem.error import BadRequestProblem, ServerProblem
from fastapi_problem.handler import add_exception_handler, new_exception_handler

logging.getLogger("uvicorn.error").disabled = True


class KnownProblem(BadRequestProblem):
    title = "Something we know about happened."


class KnownServerProblem(ServerProblem):
    title = "Something you can't do anything about happened."


app = fastapi.FastAPI()

eh = new_exception_handler()
add_exception_handler(app, eh)


@app.get("/user-error")
async def user_error() -> dict:
    raise KnownProblem("A known user error use case occurred.")


@app.get("/server-error")
async def server_error() -> dict:
    raise KnownServerProblem("A known server error use case occurred.")


if __name__ == "__main__":
    app.run()
