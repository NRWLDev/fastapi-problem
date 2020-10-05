import json
import logging

from flask import Response
from werkzeug.exceptions import HTTPException

from web_error.error import HttpException


logger = logging.getLogger(__name__)


def exception_handler(exc):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    status = 500
    message = "Unhandled exception occured."
    data = {
        "message": message,
        "debug_message": str(exc),
        "code": None,
    }

    if isinstance(exc, HTTPException):
        status = exc.code
        message = exc.name
        data = {
            "code": None,
            "message": exc.name,
            "debug_message": exc.description,
        }

    if isinstance(exc, HttpException):
        data = exc.marshal()
        status = exc.status

    if status >= 500:
        logger.exception(message)

    response = Response(status=status)

    response.data = json.dumps(data)
    response.content_type = "application/json"
    return response
