from enum import Enum

from pydantic import BaseModel


class HTTPError(BaseModel):
    detail: str


class ClientErrorType(Enum):
    INVALID_INPUT = 1
    UNAUTHORIZED = 2
    FORBIDDEN = 3
    NOT_FOUND = 4


class ClientError(Exception):
    """Exception raised when there is an error caused by the client.

    Attributes:
        client_error_type -- Enum that identifies the specific error.
        message -- Human readable message to provide information about the error.
    """

    def __init__(self, client_error_type: ClientErrorType, message: str = ""):
        self.client_error_type: ClientErrorType = client_error_type
        self.message = message

        super().__init__(message)
