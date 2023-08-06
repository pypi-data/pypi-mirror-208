import logging
from typing import NoReturn

from elefantolib import constants, exceptions
from elefantolib.auth import consumer, user

import jwt


logger = logging.getLogger(__name__)


class UserTokenService:

    def extract_token(self, token: str | None = None) -> dict | NoReturn:
        if not token:
            raise exceptions.EmptyTokenError()

        parts = token.split()

        if len(parts) != 2:
            raise exceptions.TokenLengthError(token)

        if parts[0] not in constants.TOKEN_HEADER_TYPES:
            raise exceptions.UnsupportedTokenType(token)

        jwt_consumer = consumer.Consumer.from_token(parts[1])

        payload = jwt.decode(
            jwt=parts[1],
            key=jwt_consumer.secret,
            algorithms=[constants.ALGORITHM],
            issuer=jwt_consumer.key,
            options={
                'verify_exp': True,
                'verify_iss': True,
            },
        )

        if tuple(payload.get('consumer', {}).keys()) != ('id', 'name'):
            raise exceptions.InvalidConsumerPayloadError

        return payload

    def extract_user(self, token: str = None) -> user.BaseUser:
        payload = self.extract_token(token)

        if 'user' not in payload:
            return user.AnonymousUser()

        return user.User(**payload['user'])
