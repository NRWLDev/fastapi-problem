class HttpException(Exception):
    """
    A base exception designed to support all API error handling.
    All exceptions should inherit from this or a subclass of it (depending on the usage),
    this will allow all apps and libraries to maintain a common exception chain
    """
    def __init__(self, message, debug_message=None, code=None, status=500):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.debug_message = debug_message

    def marshal(self):
        return {
            "code": self.code,
            "message": self.message,
            "debug_message": self.debug_message,
        }


class HttpCodeException(HttpException):
    status = None
    code = None
    message = None

    def __init__(self, debug_message=None):
        super().__init__(self.message, debug_message, self.code, self.status)


class ServerException(HttpCodeException):
    status = 500


class BadRequestException(HttpCodeException):
    status = 400


class UnauthorisedException(HttpCodeException):
    status = 401


class NotFoundException(HttpCodeException):
    status = 404
