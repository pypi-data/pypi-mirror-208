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


class TokenError(PyJWTError, ClientError):
    STATUS = codes.UNAUTHORIZED


class EmptyTokenError(TokenError):
    STATUS = codes.UNAUTHORIZED

    def __str__(self):
        return 'Token is not provided'


class TokenLengthError(TokenError):
    STATUS = codes.UNAUTHORIZED

    def __init__(self, token):
        self.length = token.split()

    def __str__(self):
        return f'Token must contain 2 parts, got {self.length}'


class UnsupportedTokenType(TokenError):
    STATUS = codes.UNAUTHORIZED

    def __init__(self, token):
        self.type = token.split()[0]

    def __str__(self):
        return f'Supported token types is {TOKEN_HEADER_TYPES}, got {self.type}'


class InvalidSignatureError(TokenError):
    STATUS = codes.UNAUTHORIZED

    def __str__(self):
        return 'Error decoding signature'


class InvalidConsumerPayloadError(TokenError):
    STATUS = codes.UNAUTHORIZED

    def __str__(self):
        return 'Invalid consumer payload'
