import io
import json
import logging
import selectors
import socket
from typing import Optional

from .game_connection import GameConnection, ConnectionClosed


_DEFAULT_PORT = 10019
_ENCODING = "UTF-8"
_LENGTH_BYTES = 2
_LENGTH_ORDER = "big"

_PATH_KEY = "path"
_TOKEN_KEY = "token"
_STATUS_KEY = "status"
_REASON_KEY = "reason"
_OK_STATUS = "ok"
_ERROR_STATUS = "error"

logger = logging.getLogger(__name__)


class TcpGameConnection(GameConnection):
    """ A GameConnection that is implemented using a TCP socket """

    HANDSHAKE_DELAY = 5000

    def __init__(self, server_host: str, server_port: int, path: str, token: str = None):
        self.server_host = server_host
        self.server_port = server_port if server_port else _DEFAULT_PORT
        self.path = path
        self.token = token
        self.local_address = ("0.0.0.0", 0)
        self._selector: selectors.DefaultSelector = None
        self._socket: socket.socket = None
        self._stream: io.IOBase = None

    def _handshake(self):
        self.send(json.dumps({_PATH_KEY: self.path, _TOKEN_KEY: self.token}))
        try:
            response = json.loads(self.recv(self.HANDSHAKE_DELAY))
            status = response[_STATUS_KEY]
            if status == _ERROR_STATUS:
                reason = response.get(_REASON_KEY, "unknown reason")
                logger.error(f"authorization handshake failed: {reason}")
                raise ConnectionClosed(response)
            if status != _OK_STATUS:
                logger.warning(f"authorization handshake response was not 'ok': {status}")
            logger.debug("authorization handshake successful")
        except (json.JSONDecodeError, KeyError) as err:
            message = "authorization handshake response not well formed"
            logger.error(message)
            raise ConnectionClosed(message)

    def open(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.bind(self.local_address)
            self._socket.connect((self.server_host, self.server_port))
            self._stream = self._socket.makefile("rb", buffering=False)
            self._selector = selectors.DefaultSelector()
            self._selector.register(self._socket, selectors.EVENT_READ)
            if self.token:
                self._handshake()
        except OSError as err:
            logger.error(f"error opening socket: {err}")
            self._socket.close()
            raise ConnectionClosed()

    def close(self):
        self._socket.close()

    def send(self, message: str):
        data = message.encode(_ENCODING)
        buf = bytearray()
        buf.extend(len(data).to_bytes(_LENGTH_BYTES, _LENGTH_ORDER))
        buf.extend(data)
        try:
            self._socket.sendall(buf)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"sent: {message}")
        except OSError as err:
            logger.error(f"error sending message: {err}: {message}")
            self._socket.close()
            raise ConnectionClosed

    def recv(self, timeout=None) -> Optional[str]:
        if not self._selector.select(timeout):
            return None

        data = None
        try:
            length_bytes = self._stream.read(2)
            if not length_bytes:
                raise ConnectionClosed()

            message_length = int.from_bytes(length_bytes, _LENGTH_ORDER)
            data = self._stream.read(message_length)
            message = data.decode(_ENCODING)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"received: {message}")
            return message
        except UnicodeDecodeError as err:
            logger.error(f"error decoding message: {err}: {data}")
        except OSError as err:
            logger.error(f"error receiving message: {err}")
            self._socket.close()
            raise ConnectionClosed

