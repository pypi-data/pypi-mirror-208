from elefantolib.constants import TOKEN_HEADER_TYPES

from httpx import codes

from jwt import PyJWTError


class BaseDetailedException(Exception):

    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code

    def __repr__(self) -> str:
        return f'{self.status_code}: {self.detail}'


class ClientError(BaseDetailedException):
    STATUS = codes.BAD_REQUEST

    def __init__(self, detail: str = 'invalid request', status_code: int = codes.BAD_REQUEST):
        super().__init__(detail, status_code)


class EmptyTokenError(PyJWTError, ClientError):
    STATUS = codes.UNAUTHORIZED

    def __str__(self):
        return 'Token is not provided'


class TokenLengthError(PyJWTError, ClientError):
    STATUS = codes.UNAUTHORIZED

    def __init__(self, token):
        self.length = token.split()

    def __str__(self):
        return f'Token must contain 2 parts, got {self.length}'


class UnsupportedTokenType(PyJWTError, ClientError):
    STATUS = codes.UNAUTHORIZED

    def __init__(self, token):
        self.type = token.split()[0]

    def __str__(self):
        return f'Supported token types is {TOKEN_HEADER_TYPES}, got {self.type}'


class InvalidConsumerCredentialError(PyJWTError, ClientError):
    STATUS = codes.UNAUTHORIZED

    def __str__(self):
        return 'Invalid consumer credential'


class InvalidConsumerPayloadError(PyJWTError, ClientError):
    STATUS = codes.UNAUTHORIZED

    def __str__(self):
        return 'Invalid consumer payload'
