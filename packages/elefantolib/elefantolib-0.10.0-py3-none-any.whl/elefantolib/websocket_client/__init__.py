from typing import Any

from elefantolib import constants


class BaseWebsocketClient:

    def __init__(self, service_name: str, platform_context: dict[str, Any], api_url: str = None):
        self.service_name = service_name
        self.platform_context = platform_context

        ws_url = api_url or constants.SERVICE_MAIN_URL.format(service_name)
        self.ws_url = ws_url.replace('http', 'ws')
