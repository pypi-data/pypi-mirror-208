import logging

import websockets
from websockets.sync.client import connect as ws_connect

from .game_connection import GameConnection, ConnectionClosed

DEFAULT_PORT = 10020

logger = logging.getLogger(__name__)


class WsGameConnection(GameConnection):
    """ A GameConnection that is implemented using a WebSocket """

    def __init__(self, scheme: str, server_host: str, server_port: int, path: str, token: str = None):
        self.url = f"{scheme}://{server_host}:{server_port if server_port else DEFAULT_PORT}{path}"
        self.token = token
        self._connection: websockets.sync.client.ClientConnection = None

    def open(self):
        try:
            additional_headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            self._connection = ws_connect(self.url, additional_headers=additional_headers)
            logger.debug("authorization handshake successful")
        except websockets.ConnectionClosed as err:
            logger.error(f"error connecting: {err}")
            raise ConnectionClosed()

    def close(self):
        self._connection.close()

    def send(self, message: str):
        try:
            self._connection.send(message)
        except websockets.ConnectionClosed as err:
            logger.error(f"error sending: {err}")
            raise ConnectionClosed() from None

    def recv(self, timeout=None) -> str:
        try:
            return self._connection.recv(timeout)
        except websockets.ConnectionClosed:
            raise ConnectionClosed() from None
        except TimeoutError:
            return None
