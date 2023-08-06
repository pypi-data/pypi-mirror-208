"""Exceptions module"""

from http import HTTPStatus


class ConstellationException(Exception):
    """Root class of all exceptions thrown by the constellation client"""

    def __init__(self, message, status_code):
        super().__init__()
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return "{} (StatusCode: {})".format(self.message, self.status_code)


class ConstellationInvalidResponseException(ConstellationException):
    """Thrown when constellation gives an unexpected response"""

    def __init__(self, description, response):
        super().__init__(
            message="{}.  Constellation response: {}".format(description, response),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


class ConstellationInvalidMethodException(ConstellationException):
    """Thrown when attempting an invalid http method for the call to constellation"""

    def __init__(self, method, endpoint):
        super().__init__(
            message="The method {} is not support for the endpoint {}.  Please update your call and try again".format(
                method, endpoint
            ),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


class ConstellationMissingFieldException(ConstellationException):
    """Thrown when a required field is missing"""

    def __init__(self, description, field_name):
        super().__init__(
            message="Missing field: {} when {}".format(field_name, description),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


class ConstellationNotLoggedInException(ConstellationException):
    """Thrown when the user has not logged in and an auth token is required to perform the requested action."""

    def __init__(self):
        super().__init__(
            message="You are not logged in.  Please call login() or set_auth_token() and try again.",
            status_code=HTTPStatus.UNAUTHORIZED,
        )


class ConstellationObjectDoesNotExistException(ConstellationException):
    """Thrown when constellation attemping to download an object that does not exist"""

    def __init__(self, object_id):
        super().__init__(
            message="The object {} does not exist or is not accessible by you.  Please remove it and retry your request.".format(
                object_id
            ),
            status_code=HTTPStatus.NOT_FOUND,
        )


class VariableUnitValueUnparsableExpressionException(BaseException):
    """Thrown when the supplied expression cannot be parsed"""

    def __init__(self, message, expression):
        self._message = message
        self._expression = expression

    def __str__(self):
        return (
            "VariableUnitValueUnparsableExpressionException: "
            + self._message
            + " for expression: "
            + self._expression
        )


class BinaryObjectRepresetationUnknownTokenType(BaseException):
    """Thrown when an unknown token type is encountered.

    Fixing this will require an update to the parser to handle the type"""

    def __init__(self, token_char, token):
        self._token_char = token_char
        self._token = token

    def __str__(self):
        return (
            "BinarnyObjectRepresentationUnknownTokenType: "
            + self._token_char
            + " for token "
            + self._token
        )
