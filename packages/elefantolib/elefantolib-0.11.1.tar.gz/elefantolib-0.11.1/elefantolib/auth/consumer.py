import datetime as dt
import os
from calendar import timegm

from elefantolib import constants, exceptions

import httpx

import jwt


_consumer_cache = {}


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
            payload = jwt.decode(
                token,
                algorithms=[constants.ALGORITHM],
                options={'verify_signature': False},
            )
        except Exception:
            raise jwt.InvalidIssuerError

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
            'iat': timegm(now.utctimetuple()),
            'exp': timegm((now + dt.timedelta(seconds=ttl)).utctimetuple()),
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

        if consumer_name in _consumer_cache:
            jwt_config = _consumer_cache[consumer_name]
        else:
            jwt_config = cls.send_request(consumer_name)

        if key != jwt_config['key']:
            raise jwt.InvalidIssuerError

        _consumer_cache[consumer_name] = jwt_config

        return jwt_config

    @classmethod
    def send_request(cls, consumer_name):
        kong_url = os.environ.get('KONG_ADMIN_URL', 'http://kong:8001')

        try:
            response = httpx.get(f'{kong_url}/consumers/{consumer_name}/jwt')
            response.raise_for_status()

            return response.json()['data'][0]
        except Exception:
            raise exceptions.InvalidConsumerCredentialError
