import json
import logging
import selectors
import socket
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict

import websockets
from websockets.sync.server import ServerConnection

logger = logging.getLogger(__name__)


class ConnectionClosed(ConnectionError):
    """ An exception that is raised whenever a GameConnection is closed  """
    pass


class ConnectionClosedError(ConnectionClosed):
    """ An exception that is raised whenever a GameConnection is closed due to a communication error """
    pass


class ConnectionClosedOK(ConnectionClosed):
    """ An exception that is raised whenever a GameConnection is closed under normal circumstances """
    pass


class GameConnection(ABC):
    """ An abstract base for game connection implementations """

    def __init__(self, claims: Dict = None):
        self.claims = claims

    @property
    def gid(self):
        """ Gets the game ID specified for this connection """
        return self.claims["aud"] if self.claims else None

    @property
    def uid(self):
        """ Gets the user ID of the user that was authenticated for this connection. """
        return self.claims["sub"] if self.claims else None

    @property
    def players(self):
        """ Gets the user IDs of the players in the game associated with this connection """
        return self.claims["ply"] if self.claims else None

    @abstractmethod
    def send(self, message: Any) -> None:
        """
        Sends any Python object that is representable in JSON as a message.
        :param message: any Python object (even None) that is to be sent
        :raises ConnectionClosed: if the connection was closed before the message could be sent
        """
        pass

    @abstractmethod
    def recv(self, timeout: int = None) -> Any:
        """
        Receives a JSON-encoded message and returns the resulting Python object
        :param timeout: a timeout (in seconds) after which the call will raise a TimeoutError if no message is received;
           by default (timeout=None) a call to this method will block until a message is received
        :return: a Python representation of the received message (which may be None)
        :raises TimeoutError: if no message was received within the specified timeout
        :raises ConnectionClosedOK: if the connection was closed before a message could be received
        :raises ConnectionClosedError: if any other OS error occurs in receiving the message
        :raises UnicodeDecodeError: if the received message cannot be decoded as UTF-8
        :raises json.JSONDecodeError: if the received message cannot be successfully decoded as JSON
        :raises : if the received message cannot be successfully decoded as JSON
        """
        pass


class TcpGameConnection(GameConnection):
    """ A GameConnection implemented over a TCP socket """

    ENCODING = "UTF-8"
    LENGTH_BYTES = 2
    LENGTH_ORDER = "big"
    HANDSHAKE_DELAY = 5000

    def __init__(self, stream_socket: socket.socket, peer_address: tuple[str, int]):
        super().__init__()
        self._socket = stream_socket
        self._peer_address = peer_address
        self._selector = selectors.DefaultSelector()
        self._selector.register(self._socket, selectors.EVENT_READ)
        self._stream = stream_socket.makefile("rb", buffering=False)

    def _handshake_ok(self):
        self.send({"status": "ok"})
        logger.debug("authorization handshake successful")

    def _handshake_error(self, reason):
        logger.error(reason)
        self.send({"status": "error", "reason": reason})
        raise ConnectionClosedError(reason)

    def handshake(self, on_authenticate: Callable[[str, str], Dict]):
        auth = self.recv(self.HANDSHAKE_DELAY)
        try:
            path = auth["path"]
            gid = path.split("/")[-1]
            token = auth["token"]
            self.claims = on_authenticate(gid, token)
            if self.claims:
                self._handshake_ok()
            else:
                self._handshake_error("authentication failed")
        except (KeyError, json.JSONDecodeError):
            self._handshake_error("authorization request not well formed")

    def send(self, message: Any) -> None:
        message_text = json.dumps(message)
        message_data = message_text.encode(self.ENCODING)
        message_length = len(message_data)
        buf = bytearray()
        buf.extend(message_length.to_bytes(self.LENGTH_BYTES, self.LENGTH_ORDER))
        buf.extend(message_data)
        try:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"send {self}: {message_text}")
            self._socket.sendall(buf)
        except ConnectionError:
            self._socket.close()
        except OSError as err:
            self._socket.close()
            raise ConnectionError(err)

    def recv(self, timeout: int = None) -> Any:
        if self._selector.select(timeout):
            try:
                length_bytes = self._stream.read(self.LENGTH_BYTES)
                if not length_bytes:
                    raise ConnectionClosedOK()
                message_length = int.from_bytes(length_bytes, self.LENGTH_ORDER)
                message_data = self._stream.read(message_length)
                if not message_data:
                    raise ConnectionClosedOK()
                message_text = message_data.decode(self.ENCODING)
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"recv {self}: {message_text}")
                return json.loads(message_text)
            except (ConnectionError, OSError) as err:
                self._socket.close()
                raise ConnectionClosedError(err)
        else:
            raise TimeoutError()

    def __str__(self):
        return f"tcp {self._peer_address}"


class WsGameConnection(GameConnection):
    """ A GameConnection implemented over a WebSocket """

    def __init__(self, connection: ServerConnection):
        # noinspection PyUnresolvedReferences
        super().__init__(connection.request.claims)
        self._id = connection.id
        self._peer_address = connection.remote_address
        self._connection = connection

    def send(self, message: Any) -> None:
        message_text = json.dumps(message)
        try:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"send {self}: {message_text}")
            self._connection.send(message_text)
        except websockets.ConnectionClosedError:
            raise ConnectionClosedError()
        except websockets.ConnectionClosedOK:
            raise ConnectionClosedOK()

    def recv(self, timeout: int = None) -> Any:
        try:
            message_text = self._connection.recv(timeout)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"recv {self}: {message_text}")
            return json.loads(message_text)
        except websockets.ConnectionClosedError:
            raise ConnectionClosedError()
        except websockets.ConnectionClosedOK:
            raise ConnectionClosedOK()

    def __str__(self):
        return f"ws {self._peer_address}"
