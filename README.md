# Web Errors v0.3.0
[![image](https://img.shields.io/pypi/v/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)
[![image](https://img.shields.io/pypi/l/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)
[![image](https://img.shields.io/pypi/pyversions/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)
![style](https://github.com/EdgyEdgemond/web-error/workflows/style/badge.svg)
![tests](https://github.com/EdgyEdgemond/web-error/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/EdgyEdgemond/web-error/branch/master/graph/badge.svg)](https://codecov.io/gh/EdgyEdgemond/web-error)

`web_error` is a set of exceptions and handlers for use in web apis to support easy error management and responses

Each exception easily marshals to JSON for use in api errors. Handlers for different web frameworks are provided.


## Errors

The base `web_error.error.HttpException` accepts a `message`, `debug_message`, `code` and `status` (default 500)

And will render a response with status as the status code:

```json
{
    "code": "code",
    "message": "message",
    "debug_message": "debug_message",
}
```

Some convenience Exceptions are provided, to create custom error subclass these
and define `message` and `code` attributes.

* `web_error.error.ServerException` provides status 500 errors
* `web_error.error.BadRequestException` provides status 400 errors
* `web_error.error.UnauthorisedException` provides status 401 errors
* `web_error.error.NotFoundException` provides status 404 errors

### Custom Errors

Subclassing the convenience classes provide a simple way to consistently raise the same error
and message.

Code is an optional attribute to provide a unique value to parse in a frontend/client instead of
matching against messages.

```python
from web_error.error import NotFoundException


class UserNotFoundError(NotFoundException):
    message = "User not found."
    code = "E001"
```

## Pyramid

Include the pyramid exception handlers in your config.

```python
def main(global_config, **config_blob):
    config = Configurator(settings=config_blob)

    ...

    config.scan("web_error.handler.pyramid")

    return config.make_wsgi_app()
```

This will handle all unexpected errors, and any app specific errors.

```python
@view_config(route_name="test", renderer="json")
def test(request):
    raise UserNotFoundError("debug message")
```


## Flask

Register the error handler with your application

```python
app.register_error_handler(Exception, web_error.handler.flask.exception_handler)
```

## Aiohttp

Decorate your views with the error handler.

```python
@web_error.handler.aiohttp.view_error_handler
async def user(self):
    raise UserNotFoundError("debug message")
```
