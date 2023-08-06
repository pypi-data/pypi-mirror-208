import datetime as dt
import os

from elefantolib import exceptions

import httpx

import jwt


class Consumer:

    def __init__(self, consumer_id: str, consumer_name: str, key: str, secret: str):
        self.consumer_id = consumer_id
        self.consumer_name = consumer_name
        self._key = key
        self._secret = secret

    @classmethod
    def from_name(cls, consumer_name: str, key: str):
        consumer_config = cls._get_jwt_config(consumer_name, key)

        return cls(
            consumer_id=consumer_config['id'],
            consumer_name=consumer_name,
            key=consumer_config['key'],
            secret=consumer_config['secret'],
        )

    @classmethod
    def from_token(cls, token: str):
        try:
            payload = jwt.decode(token, algorithms=['HS256'], options={'verify_signature': False})
        except Exception:
            raise exceptions.InvalidSignatureError

        try:
            consumer_name = payload['consumer']['name']
            consumer_key = payload['iss']
        except KeyError:
            raise exceptions.InvalidConsumerPayloadError

        return cls.from_name(consumer_name, consumer_key)

    @property
    def key(self):
        return self._key

    @property
    def secret(self):
        return self._secret

    def generate_jwt_payload(self, ttl: int) -> dict:
        now = dt.datetime.utcnow()

        return {
            'iss': self._key,
            'iat': now,
            'exp': now + dt.timedelta(seconds=ttl),
            'consumer': {
                'id': str(self.consumer_id),
                'name': self.consumer_name,
            },
        }

    @classmethod
    def _get_jwt_config(cls, consumer_name: str, key: str) -> dict:
        """
        Get JWT config for consumer with provided `consumer_name` from Kong.
        """
        kong_url = os.environ.get('KONG_ADMIN_URL', 'http://kong:8001')

        try:
            response = httpx.get(f'{kong_url}/consumers/{consumer_name}/jwt')
            response.raise_for_status()
            jwt_config = response.json()['data'][0]
        except Exception:
            raise Exception('Invalid consumer credentials.')

        if key != jwt_config['key']:
            raise Exception('Invalid consumer payload: keys does not match.', 'invalid_payload')

        return jwt_config
