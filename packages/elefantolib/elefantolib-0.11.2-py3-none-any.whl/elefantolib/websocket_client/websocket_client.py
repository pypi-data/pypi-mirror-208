from typing import Callable

from elefantolib.websocket_client import BaseWebsocketClient

import websockets


class WebsocketClient(BaseWebsocketClient):

    async def ws(self, path: str, callback: Callable, *args, **kwargs):
        url = f'{self.ws_url}/{path}'
        async with websockets.connect(url) as ws_connect:
            await callback(ws_connect, *args, **kwargs)
