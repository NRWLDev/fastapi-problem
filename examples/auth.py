"""
Run this example:
$ fastapi dev examples/auth.py

To see a 401 response.
$ curl http://localhost:8000/authorized

To see a 403 response.
$ curl http://localhost:8000/authorized -H "Authorization: Bearer not-permitted"

To see an authorized response.
$ curl http://localhost:8000/authorized -H "Authorization: Bearer permitted"
"""

import fastapi
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_problem.error import (
    ForbiddenProblem,
    UnauthorisedProblem,
)
from fastapi_problem.handler import add_exception_handler


class AuthorizationRequiredError(UnauthorisedProblem):
    title = "Authorization token required."


class PermissionRequiredError(ForbiddenProblem):
    title = "Permission required."


async def check_auth(
    request: fastapi.Request,
    authorization: HTTPAuthorizationCredentials = fastapi.Depends(HTTPBearer(auto_error=False)),
) -> bool:
    if authorization is None:
        msg = "Missing Authorization header."
        raise AuthorizationRequiredError(msg)

    if authorization.credentials != "permitted":
        msg = "No active permissions."
        raise PermissionRequiredError(msg)

    return True


app = fastapi.FastAPI()

add_exception_handler(
    app,
)


@app.get("/authorized")
async def authorized(
    authorized=fastapi.Depends(check_auth),
) -> dict:
    return {"authorized": authorized}
