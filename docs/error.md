# Errors

The base `fastapi_problem.error.HttpException` accepts a `title`, `details`, `status`
(default 500) and optional `**kwargs`. An additional `code` can be passed in,
which will be used as the `type`, if not provided the `type` is derived from
the class name.

And will return a JSON response with `exc.status` as the status code and response body:

```json
{
    "type": "an-exception",
    "title": "title",
    "details": "details",
    "status": 500,
    "extra-key": "extra-value",
    ...
}
```

Derived types are generated using the class name after dropping `...Error` from
the end, and converting to `kebab-case`. i.e. `PascalCaseError` will derive the
type `pascal-case`. If the class name doesn't suit your purposes, an optional
`code` attribute can be set with the desired value of there response `type`
field.

Some convenience Exceptions are provided with predefined `status` attributes.
To create custom errors subclasss these and define the `title` attribute.

* `fastapi_problem.error.ServerException` provides status 500 errors
* `fastapi_problem.error.BadRequestException` provides status 400 errors
* `fastapi_problem.error.UnauthorisedException` provides status 401 errors
* `fastapi_problem.error.NotFoundException` provides status 404 errors

## Custom Errors

Subclassing the convenience classes provide a simple way to consistently raise the same error
with details/extras changing based on the raised context.

```python
from fastapi_problem.error import NotFoundException


class UserNotFoundError(NotFoundException):
    title = "User not found."

raise UserNotFoundError(details="details")
```

```json
{
    "type": "user-not-found",
    "title": "User not found",
    "details": "details",
    "status": 404,
}
```

Whereas a defined `code` will be used in the output.

```python
class UserNotFoundError(NotFoundException):
    title = "User not found."
    code = "cant-find-user"

raise UserNotFoundError(details="details")
```

```json
{
    "type": "cant-find-user",
    "title": "User not found",
    "details": "details",
    "status": 404,
}
```

If additional kwargs are provided when the error is raised, they will be
included in the output (ensure the provided values are json seriablizable.


```python
raise UserNotFoundError(details="details", user_id="1234", metadata={"hello": "world"})
```

```json
{
    ...
    "details": "details",
    "user_id": "1234",
    "metadata": {"hello": "world"},
}
```
