from typing import Any


class ContextService:

    def __init__(self, http_client, ws_client, context: dict[str, Any]):
        self._http_client = http_client
        self._ws_client = ws_client
        self._context = context
        self.__services = {}

    def __getattr__(self, item):
        if service := self.__services.get(item):
            return service

        self.__services[item] = type(
            item,
            (self._http_client, self._ws_client),
            {'service_name': item, 'platform_context': self._context},
        )

        return self.__services[item]

    def __getitem__(self, item):
        return getattr(self, item)
