from typing import Any, Protocol


class Provider(Protocol):

    def auth_token(self):
        ...

    def correlation_id(self):
        ...

    def locale(self):
        ...


class DictProvider:

    def __init__(self, context: dict[str, Any]):
        self.context = context

    @property
    def auth_token(self):
        return self.context.get('auth_token')

    @property
    def correlation_id(self):
        return self.context.get('correlation_id')

    @property
    def locale(self):
        return self.context.get('locale')
