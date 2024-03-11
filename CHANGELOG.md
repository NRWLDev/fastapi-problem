# Changelog

## v0.6.7 - 2024-03-11

### Bug fixes

- Cleanup legacy warning detection [[9c54796](https://github.com/EdgyEdgemond/web-error/commit/9c54796458082a1a9f7b265c33348335f65f5e44)]

## v0.6.6 - 2024-03-08

### Bug fixes

- Clean up message deprecation detection [[c2a0e3f](https://github.com/EdgyEdgemond/web-error/commit/c2a0e3f552fad60e0ea73b449e269c89c3c2f43c)]

## v0.6.5 - 2024-03-08

### Bug fixes

- Expose legacy attributes, accessing new attributes. [[30c3682](https://github.com/EdgyEdgemond/web-error/commit/30c3682ea9526b6c2a4b180cd928becd69396961)]

## v0.6.4 - 2024-03-08

### Bug fixes

- Handle legacy exception definitions with message attribute [[c07215c](https://github.com/EdgyEdgemond/web-error/commit/c07215cc4ec9e10953abded8311a93717704a324)]

## v0.6.3 - 2024-03-08

### Bug fixes

- Support legacy init [[e83a8f8](https://github.com/EdgyEdgemond/web-error/commit/e83a8f8b29b11694414b20e2e2ac1856b61dbb0c)]

## v0.6.2 - 2024-03-04

### Features and Improvements

- Attach exception handlers to an active app, rather than providing to `__init__` [[#23](https://github.com/EdgyEdgemond/web-error/issues/23)] [[3d61d82](https://github.com/EdgyEdgemond/web-error/commit/3d61d82be86e12ee477cb5737e8085ff8982167f)]

## v0.6.1 - 2024-02-29

### Bug fixes

- Derive title/type from unexpected error status_codes.  [[#19](https://github.com/EdgyEdgemond/web-error/issues/19)] [[a62d99a](https://github.com/EdgyEdgemond/web-error/commit/a62d99a64b02d79a0e54ceaab7c3d7bc689b56e1)]

## v0.6.0

### Features and Improvements

- **Breaking:** Drop support for aiohttp, flask and pyramid. Refactor fastapi/starlette interface. [[#16](https://github.com/EdgyEdgemond/web-error/issues/16)]
- Default to RFC9457 response formats, optional legacy generator kwarg can be provided to maintain old response formats. [[#15](https://github.com/EdgyEdgemond/web-error/issues/15)]

## v0.5.6

## v0.5.5

## v0.5.4

## v0.5.3

## v0.5.2

## v0.5.1

## v0.5.0

### Features and Improvements

- Introduce ruff, black, pre-commit. Drop support for py 3.7 and earlier. [[#13](https://github.com/EdgyEdgemond/web-error/issues/13)]

## v0.4.2

### Bug fixes

- Handle starlette core exceptions [[#11](https://github.com/EdgyEdgemond/web-error/issues/11)]

## v0.4.1

## v0.4.0

### Features and Improvements

- Migrate fastapi handler to starlette handler, extend starlette handler to support fastapi. [[#9](https://github.com/EdgyEdgemond/web-error/issues/9)]

## v0.3.1

### Bug fixes

- Generate fastapi handler with cors support. [[#7](https://github.com/EdgyEdgemond/web-error/issues/7)]

## v0.3.0

### Features and Improvements

- Add support for reraising from an error response from another api. [[#5](https://github.com/EdgyEdgemond/web-error/issues/5)]

## v0.2.2

### Bug fixes

- Support RequestValidationError exceptions in fastapi handler. [[#4](https://github.com/EdgyEdgemond/web-error/issues/4)]

## v0.2.1

### Bug fixes

- Bugfix for fastapi exception logging [[#2](https://github.com/EdgyEdgemond/web-error/issues/2)]

## v0.2.0

### Features and Improvements

- Add handler to support fastapi [[#2](https://github.com/EdgyEdgemond/web-error/issues/2)]

## v0.1.1

## v0.1.0

### Features and Improvements

- Add in pyramid exception handlers [[#1](https://github.com/EdgyEdgemond/web-error/issues/1)]

## v0.0.2

### Bug fixes

- Initial code release
