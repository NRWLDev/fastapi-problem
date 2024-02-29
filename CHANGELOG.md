# Changelog

## v0.6.1 - 2024-02-29

### Bug fixes

- Derive title/type from unexpected error status_codes.  [[#19](https://github.com/EdgyEdgemond/web-error/issues/19)] [[a62d99a](https://github.com/EdgyEdgemond/web-error/commit/a62d99a64b02d79a0e54ceaab7c3d7bc689b56e1)]

## v0.6.0

### Features and Improvements

- Default to RFC9457 response formats, optional legacy generator kwarg can be provided to maintain old response formats. [[#15](https://github.com/EdgyEdgemond/web-error/issues/15)]
- Drop support for aiohttp, flask and pyramid. Refactor fastapi/starlette interface. [[#16](https://github.com/EdgyEdgemond/web-error/issues/16)]

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

- Initial code release [[#initial](https://github.com/EdgyEdgemond/web-error/issues/initial)]
