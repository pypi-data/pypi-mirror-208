from typing import Iterable, NoReturn

from elefantolib import exceptions, provider
from elefantolib.auth import UserTokenService
from elefantolib.context import context_service
from elefantolib.http_client import httpx_client
from elefantolib.websocket_client import websocket_client


class BaseContext:
    HTTP_CLIENT = None
    WEBSOCKET_CLIENT = None
    CONTEXT_ATTRIBUTES = (
        'auth_token',
        'correlation_id',
        'locale',
    )
    REQUIRED_ATTRIBUTES = (
        'auth_token',
        'correlation_id',
        'locale',
    )
    user = None

    def __init__(self, pvr: provider.Provider):
        for attribute in self.CONTEXT_ATTRIBUTES:
            setattr(self, attribute, getattr(pvr, attribute, None))

        self.services = context_service.ContextService(
            self.HTTP_CLIENT, self.WEBSOCKET_CLIENT, self.context,
        )

    @property
    def context(self):
        return {a: getattr(self, a) for a in self.CONTEXT_ATTRIBUTES}

    def validate(self, required_attrs: Iterable = None) -> None | NoReturn:
        required_attrs = required_attrs or self.REQUIRED_ATTRIBUTES

        for required_attr in required_attrs:
            if required_attr == 'auth_token' and (token := getattr(self, required_attr, None)):
                uts = UserTokenService()
                self.user = uts.extract_user(token)
                continue

            if getattr(self, required_attr, None) is not None:
                continue

            raise exceptions.ClientError(f'{required_attr} must be set for this request.')

        return None


class PlatformContext(BaseContext):
    HTTP_CLIENT = httpx_client.HttpxClient
    WEBSOCKET_CLIENT = websocket_client.WebsocketClient


class AsyncPlatformContext(BaseContext):
    HTTP_CLIENT = httpx_client.AsyncHttpxClient
    WEBSOCKET_CLIENT = websocket_client.WebsocketClient
