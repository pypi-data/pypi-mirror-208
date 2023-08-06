import logging
from typing import NoReturn

from elefantolib.auth import user
from elefantolib.constants import ALGORITHM, ISSUER, SECRET, TOKEN_HEADER_TYPES
from elefantolib.exceptions import EmptyTokenError, TokenError, TokenLengthError, UnsupportedTokenType

import jwt


logger = logging.getLogger(__name__)


class UserTokenService:
    SECRET = SECRET
    ALGORITHM = ALGORITHM
    ISSUER = ISSUER

    def extract_token(self, token: str | None = None) -> dict | NoReturn:

        try:
            if not token:
                raise EmptyTokenError()

            parts = token.split()

            if len(parts) != 2:
                raise TokenLengthError(token)

            if parts[0] not in TOKEN_HEADER_TYPES:
                raise UnsupportedTokenType(token)

            return jwt.decode(
                jwt=parts[1],
                key=self.SECRET,
                algorithms=[self.ALGORITHM],
                issuer=ISSUER,
                options={
                    'verify_exp': True,
                    'verify_iss': True,
                },
            )

        except (jwt.ExpiredSignatureError,
                jwt.InvalidIssuerError,
                jwt.InvalidSignatureError,
                jwt.InvalidSignatureError) as e:
            logger.error(TokenError(f'Problems with token: {e}'))
            raise TokenError(f'Problems with token: {e}')

    def extract_user(self, token: str = None) -> user.BaseUser:
        payload = self.extract_token(token)

        if not {'id', 'name'}.issubset(set(payload.keys())):
            return user.AnonymousUser()

        return user.User(
            payload['id'],
            payload['name'],
            payload.get('email', None),
            payload.get('permissions', set()),
        )
