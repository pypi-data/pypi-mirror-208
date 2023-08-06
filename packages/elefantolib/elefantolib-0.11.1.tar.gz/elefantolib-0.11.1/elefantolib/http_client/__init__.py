from typing import Any

from elefantolib import constants


class BaseClient:

    def __init__(self, service_name: str, platform_context: dict[str, Any], api_url: str = None):
        self.service_name = service_name
        self.api_url = api_url or constants.SERVICE_MAIN_URL.format(service_name)
        self.platform_context = platform_context

    @property
    def headers(self) -> dict[str, Any]:
        return {
            'Accept-Language': self.platform_context.get('locale'),
            'X-Correlation-Id': self.platform_context.get('correlation_id'),
        }
