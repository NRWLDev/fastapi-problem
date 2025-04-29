# Errors

The base `fastapi_problem.error.Problem` accepts a `title`, `detail`, `status`
(default 500) and optional `**kwargs`. An additional `code` can be passed in,
which will be used as the `type`, if not provided the `type` is derived from
the class name.

And will return a JSON response with `exc.status` as the status code and response body:

```json
{
    "type": "an-exception",
    "title": "title",
    "detail": "detail",
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

Some convenience Problems are provided with predefined `status` attributes.
To create custom errors subclasss these and define the `title` attribute.

* `fastapi_problem.error.ServerProblem` provides status 500 errors
* `fastapi_problem.error.RedirectProblem` provides status 301 errors
* `fastapi_problem.error.BadRequestProblem` provides status 400 errors
* `fastapi_problem.error.UnauthorisedProblem` provides status 401 errors
* `fastapi_problem.error.ForbiddenProblem` provides status 403 errors
* `fastapi_problem.error.NotFoundProblem` provides status 404 errors
* `fastapi_problem.error.ConflictProblem` provides status 409 errors
* `fastapi_problem.error.UnprocessableProblem` provides status 422 errors

## Custom Errors

Subclassing the convenience classes provide a simple way to consistently raise the same error
with detail/extras changing based on the raised context.

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

Whereas a defined `code` will be used in the output.

```python
class UserNotFoundError(NotFoundProblem):
    title = "User not found."
    type_ = "cant-find-user"

raise UserNotFoundError(detail="detail")
```

```json
{
    "type": "cant-find-user",
    "title": "User not found",
    "detail": "detail",
    "status": 404,
}
```

If additional kwargs are provided when the error is raised, they will be
included in the output (ensure the provided values are json seriablizable.


```python
raise UserNotFoundError(detail="detail", user_id="1234", metadata={"hello": "world"})
```

```json
{
    ...
    "detail": "detail",
    "user_id": "1234",
    "metadata": {"hello": "world"},
}
```

### Headers

Problem subclasses can define specific headers at definition, or provide
instance specific headers at raise. These headers will be extracted and
returned as part of the response.

Headers provided when raising will overwrite any matching headers defined on the class.

```python
class HeaderProblem(StatusProblem):
    status = 400
    headers = {"x-define-header": "value"}


raise HeaderProblem(headers={"x-instance-header": "value2"})

response.headers == {
    "x-define-header": "value",
    "x-instance-header": "value2",
}
```

### Redirects

An additional helper class `RedirectProblem` is provided for handling 3XX
problems with a `Location` header. This subclass takes an additional required
init argument `location`.

```python
class PermanentRedirect(RedirectProblem):
    status = 308
    title = "Permanent redirect"


raise PermanentRedirect("https://location", "detail of move")

e.headers == {
    "Location": "https://location",
}
```

## Error Documentation

The RFC-9457 spec defines that the `type` field should provide a URI that can
link to documentation about the error type that has occurred. By default the
Problem class provides a unique identifier for the type, rather than a full
url. If your service/project provides documentation on error types, the
documentation uri can be provided to the handler which will result in response
`type` fields being converted to a full link. The uri `.format()` will be
called with the type, title, status and any additional extras provided when the
error is raised.

```python
eh = new_exception_handler(
    documentation_uri_template="https://link-to/my/errors/{type}",
)
add_exception_handler(app, eh)
```

```json
{
    "type": "https://link-to/my/errors/an-exception",
    ...
}
```

Where a full resolvable documentation uri does not exist, the rfc allows for a
[tag uri](https://en.wikipedia.org/wiki/Tag_URI_scheme#Format).

```python
eh = new_exception_handler(
    documentation_uri_template="https://link-to/my/errors/{type}",
)
add_exception_handler(app, eh)
```

```json
{
    "type": "tag:my-domain.com,2024-01-01:an-exception",
    ...
}
```

### Strict mode

The RFC-9457 spec defines the type as requiring a URI format, when no reference
is provided, it should default to `about:blank`. Initializing the handler in
`strict_rfc9457` more requires the `documentation_uri_template` to be defined, and
in cases where the Problem doesn't explicitly define a `type_` attribute, the
type will default to `about:blank`.

```python
eh = new_exception_handler(
    documentation_uri_template="https://link-to/my/errors/{type}",
    strict_rfc9457=True,
)
add_exception_handler(app, eh)
```

```json
{
    "type": "about:blank",
    ...
}
```
