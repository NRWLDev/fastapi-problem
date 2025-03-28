# Changelog

## v0.10.7 - 2025-03-28

### Bug fixes

- Prevent request validation errors from appearing as a duplicate of internal validation errors in swagger docs. [[33](https://github.com/NRWLDev/fastapi-problem/issues/33)] [[9082dbe](https://github.com/NRWLDev/fastapi-problem/commit/9082dbefbec6777be62ef2e87b8ca442e5a67a42)]

## v0.10.6 - 2025-02-17

### Features and Improvements

- Add support for generating specific error responses for swagger. [[31](https://github.com/NRWLDev/fastapi-problem/issues/31)] [[bed7f10](https://github.com/NRWLDev/fastapi-problem/commit/bed7f100f0c1a8afab8220665e1dcb2e9b80866f)]

## v0.10.5 - 2025-02-07

### Bug fixes

- Include examples for 4xx and 5xx responses. [[234b84b](https://github.com/NRWLDev/fastapi-problem/commit/234b84b6331892f1ecefaad24357fa9b92cd9825)]

## v0.10.4 - 2025-02-07

### Features and Improvements

- Register generic 4xx and 5xx responses for paths in swagger docs. [[cc08e52](https://github.com/NRWLDev/fastapi-problem/commit/cc08e52f28b1b55cd8c2874faee610c5f81fd04e)]

## v0.10.3 - 2025-02-07

### Features and Improvements

- Register generic 4xx and 5xx responses for paths in swagger docs. [[de698cc](https://github.com/NRWLDev/fastapi-problem/commit/de698ccc61ef10e3245c5201640ecf7d418fe01f)]

## v0.10.2 - 2025-02-07

### Features and Improvements

- Replace default 422 response in swagger with an accurate Problem component. [[28](https://github.com/NRWLDev/fastapi-problem/issues/28)] [[e92514f](https://github.com/NRWLDev/fastapi-problem/commit/e92514f8b253db4b2df3a2d21135c7a75d33155c)]

## v0.10.1 - 2024-11-14

### Bug fixes

- Drop support for generate_handler to simplify interface, [[d91a703](https://github.com/NRWLDev/fastapi-problem/commit/d91a703055dbb7b221b72958e4867aae5ba3be7c)]

## v0.10.0 - 2024-11-14

### Bug fixes

- **Breaking** Remove deprecated strip_debug flags. [[908a80b](https://github.com/NRWLDev/fastapi-problem/commit/908a80b5fae7123f4a8cc5d353b0dbb8c9e4c368)]

## v0.9.6 - 2024-10-01

### Bug fixes

- Stop deprecation warnings when flag is not explicitly set. [[aaa8781](https://github.com/NRWLDev/fastapi-problem/commit/aaa8781441ba685633385c6cc2813bc1fc7da423)]

## v0.9.5 - 2024-10-01

### Bug fixes

- Update starlette-problem pin to include deprecation for strip_debug fields. [[26](https://github.com/NRWLDev/fastapi-problem/issues/26)] [[e1c5ae1](https://github.com/NRWLDev/fastapi-problem/commit/e1c5ae1aeeb284246f6cced9610460feaa870be5)]

## v0.9.4 - 2024-09-09

### Miscellaneous

- Migrate from poetry to uv for dependency and build management [[477e369](https://github.com/NRWLDev/fastapi-problem/commit/477e3698ce48bbd79575877ac5339ffde5d01087)]

## v0.9.3 - 2024-09-03

### Miscellaneous

- Update starlette-problem minimum supported version. [[c4db645](https://github.com/NRWLDev/fastapi-problem/commit/c4db64579358316942a134295a35a2e383473a36)]
- Update changelog-gen and related configuration. [[bc5f88d](https://github.com/NRWLDev/fastapi-problem/commit/bc5f88daf10c98821a9e24178e1ec5a9345ee19b)]

## v0.9.2 - 2024-08-29

### Miscellaneous

- Rename documentation_base_uri to documentation_uri_template [[cff46af](https://github.com/NRWLDev/fastapi-problem/commit/cff46afacffc5e44bcb0636f93fedb77352645ec)]

## v0.9.1 - 2024-08-29

### Bug fixes

- Update rfc9457 library and document strict mode and new uri support. [[1369d62](https://github.com/NRWLDev/fastapi-problem/commit/1369d6225a119a1f9a7020ea3862f0e64f88c156)]

## v0.9.0 - 2024-07-23

### Miscellaneous

- **Breaking:** Update rfc9457 with fix for correct response format per spec. [[8401bc7](https://github.com/NRWLDev/fastapi-problem/commit/8401bc738c7fb61bc57d738777d8b6f5c8290240)]

## v0.8.1 - 2024-06-28

### Features and Improvements

- Use underlying starlette-problem library to reduce code duplication. [[9a4165e](https://github.com/NRWLDev/fastapi-problem/commit/9a4165e3ce1e06ae3731b4529643d57c80b2e706)]

### Miscellaneous

## v0.8.0 - 2024-06-14

### Features and Improvements

- **Breaking:** Drop deprecated features from 0.7 release. [[79f1026](https://github.com/NRWLDev/fastapi-problem/commit/79f1026e4519dd8fc7ff9091060dbf595e42f3a4)]

## v0.7.20 - 2024-05-31

### Features and Improvements

- Add support for fully qualified documentation links in type. [[0d7e353](https://github.com/NRWLDev/fastapi-problem/commit/0d7e35326d1269af980d81b28545cb35a5c4cf83)]

## v0.7.19 - 2024-05-31

### Bug fixes

- Update rfc9457 and include redirect support. [[f9fe241](https://github.com/NRWLDev/fastapi-problem/commit/f9fe2411aa6d1fea0397794f318503b0cc33c005)]

### Documentation

- Expand documentation to include headers and sentry information. [[555e657](https://github.com/NRWLDev/fastapi-problem/commit/555e6578dc16c5895226bb36839b74cc0e34f537)]

## v0.7.18 - 2024-05-28

### Features and Improvements

- Allow handlers to return None to delegate handling of the exception to the next handler in the chain. [[dd3a252](https://github.com/NRWLDev/fastapi-problem/commit/dd3a25255d5d7b4a782f30e4dbb86937778227e6)]

## v0.7.17 - 2024-05-25

### Bug fixes

- Add deprecation warnings to deprecated modules. [[#15](https://github.com/NRWLDev/fastapi-problem/issues/15)] [[a23747f](https://github.com/NRWLDev/fastapi-problem/commit/a23747f82fcdbcbf35a12effc977651c0c2be936)]

## v0.7.16 - 2024-05-23

### Bug fixes

- Include Problem.headers in the JSONResponse. [[95bce0c](https://github.com/NRWLDev/fastapi-problem/commit/95bce0ca81b71eba6b7dd5dd18776f1ba8169f0f)]

## v0.7.15 - 2024-05-23

### Bug fixes

- rfc9457 now supports headers and status_code, no need to reimplement base classes. [[089c65f](https://github.com/NRWLDev/fastapi-problem/commit/089c65fdeacd589a3db5ff4e6a095b3732054a08)]

## v0.7.14 - 2024-05-22

### Bug fixes

- Remove HTTPException subclassing, and notify starlette of Problem in exception handlers to have them properly handled in sentry integration. [[b8324fa](https://github.com/NRWLDev/fastapi-problem/commit/b8324faf5c792692ad1971137a6a837b11a14010)]

## v0.7.13 - 2024-05-22

### Miscellaneous

- Multiclass inheritance from starlette.HTTPException introduces unexpected side effects in testing and middleware. [[c8b0f3d](https://github.com/NRWLDev/fastapi-problem/commit/c8b0f3d291622fccf630284e57737b006ab2a7dd)]

## v0.7.12 - 2024-05-22

### Bug fixes

- Remove __str__ implementation overrides, rely on rfc9457 implementation [[fc90194](https://github.com/NRWLDev/fastapi-problem/commit/fc901947bea38386240afea09731754bd1002191)]

## v0.7.11 - 2024-05-21

### Bug fixes

- Pin rfc9457 [[50bb647](https://github.com/NRWLDev/fastapi-problem/commit/50bb647e6130abe8e118a9f4156d5537ae8ccdcc)]

## v0.7.10 - 2024-05-21

### Bug fixes

- Make logger optional with no base logger, allow disabling logging on exceptions. [[9da8d50](https://github.com/NRWLDev/fastapi-problem/commit/9da8d50a51cc3c6d0e184ec4e374bef67936c808)]

## v0.7.9 - 2024-05-21

### Bug fixes

- Subclass rfc9457 Problems with HTTPException to support sentry_sdk starlette integrations. [[#11](https://github.com/NRWLDev/fastapi-problem/issues/11)] [[8b43192](https://github.com/NRWLDev/fastapi-problem/commit/8b43192b8336b9d94164f0d1cfad9d396a6af08c)]
- Add in py.typed file so mypy/pyright acknowledge type hints. [[#12](https://github.com/NRWLDev/fastapi-problem/issues/12)] [[010f6da](https://github.com/NRWLDev/fastapi-problem/commit/010f6da1b718d9397187fd8a71a225f8f155ad72)]

## v0.7.7 - 2024-05-16

### Features and Improvements

- Use rfc9457 library for base Problem implementation. [[a9cf622](https://github.com/NRWLDev/fastapi-problem/commit/a9cf62209155da132a98dd8a88ac59f5a14b1028)]

## v0.7.6 - 2024-05-15

### Miscellaneous

- Deprecate code in favour of type_ on base class implementations. [[fa828a2](https://github.com/NRWLDev/fastapi-problem/commit/fa828a2cf42b826018bb09769ff587bca92d146a)]

## v0.7.5 - 2024-05-13

### Bug fixes

- Fix issue where custom handlers were ignored. [[34898e7](https://github.com/NRWLDev/fastapi-problem/commit/34898e79f436847145428114bd0ca7aebde83bab)]

## v0.7.4 - 2024-05-13

### Bug fixes

- Fix typo in HttpException init. [[1c7fcf9](https://github.com/NRWLDev/fastapi-problem/commit/1c7fcf970cce7e208e0f74102e88a1574d2db2ad)]

## v0.7.3 - 2024-05-13

### Bug fixes

- Add missed ForbiddenProblem 403 convenience class. [[1c756ee](https://github.com/NRWLDev/fastapi-problem/commit/1c756eec1c9203e219eed29a10f7359c5dbcbc35)]

## v0.7.2 - 2024-05-12

### Features and Improvements

- Add support for pre/post hooks. [[#1](https://github.com/NRWLDev/fastapi-problem/issues/1)] [[a02b7cf](https://github.com/NRWLDev/fastapi-problem/commit/a02b7cf70b77feb7d300a979d27fcb9a6a0288d8)]
- Support custom exception handler functions [[#2](https://github.com/NRWLDev/fastapi-problem/issues/2)] [[95e56d1](https://github.com/NRWLDev/fastapi-problem/commit/95e56d1ca78bf11aa95c29970ba155e8e418be18)]
- Implement base error class Problem [[#3](https://github.com/NRWLDev/fastapi-problem/issues/3)] [[e35bfcf](https://github.com/NRWLDev/fastapi-problem/commit/e35bfcffccdf9b9564b4ec3dad6059c01e5680e5)]

## v0.7.1 - 2024-05-01

### Bug fixes

- Remove unused legacy warning [[f4f51f0](https://github.com/NRWLDev/fastapi-problem/commit/f4f51f087e1ed1de30d7dfbcd2a3f80181883044)]

## v0.7.0 - 2024-05-01

### Features and Improvements

- **Breaking:** Drop support for legacy modes from web_error [[89bff61](https://github.com/NRWLDev/fastapi-problem/commit/89bff61eddcb6d068c7e8a7a8cf4a231cb4bd7dc)]

## v0.6.10 - 2024-04-11

### Features and Improvements

- Support stripping debug by status code, rather than flag. [#1](https://github.com/EdgyEdgemond/web-error/issues/1) [4d76e1e](https://github.com/EdgyEdgemond/web-error/commit/4d76e1eb65efa004d62812e64d40fcc8a224405a)

## v0.6.9 - 2024-03-12

### Bug fixes

- Fix incorrect string method used in type generation [01f2c1b](https://github.com/EdgyEdgemond/web-error/commit/01f2c1b26ee296ef723d4c852dbe162e0218174f)

## v0.6.8 - 2024-03-12

### Bug fixes

- Only replace last instance of Error in class name [eff6b14](https://github.com/EdgyEdgemond/web-error/commit/eff6b149f1d72a58fa4ec0340f0a9511a88d85e1)

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
