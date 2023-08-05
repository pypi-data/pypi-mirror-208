import json
import logging
import sys
from urllib.parse import urlparse

from abc import ABC, abstractmethod
from typing import Callable
from threading import Event, Lock, Thread

from .game_connection import ConnectionClosed
from .tcp_connection import TcpGameConnection
from .ws_connection import WsGameConnection


logger = logging.getLogger(__name__)


class GameClient(ABC):
    """ An abstract base for game client implementations """

    RECV_TIMEOUT_SECONDS = 0.250

    def __init__(self, url: str, token: str = None, on_event: Callable[[dict], None] = None):
        """
        Creates a new client instance.
        :param url: URL which may use the `ws`, `wss`, or `tcp` protocol; see the README in this directory for
            more information on specifying the URL
        :param token: an optional authentication token; if specified it will be used to authenticate the client's
            connection to the server
        :param on_event: an optional callback that will be invoked (on a dedicated service thread) each time that
            an unsolicited event notification is received from the server
        """
        self.url = url
        self.token = token
        self.on_event = on_event
        parsed_url = urlparse(self.url)
        if parsed_url.scheme == "tcp":
            self._connection = TcpGameConnection(parsed_url.hostname, parsed_url.port, parsed_url.path, token)
        else:
            self._connection = WsGameConnection(parsed_url.scheme, parsed_url.hostname, parsed_url.port, parsed_url.path, token)
        self._pending_requests: list[tuple[Callable[[dict], None], Callable[[dict], None]]] = []
        self._thread = Thread(target=self._run, daemon=True)
        self._shutdown = Event()
        self._lock = Lock()

    @abstractmethod
    def is_event(self, message: dict):
        """
        Examines the contents of the given message to determine whether it represents an unsolicited
        event notification or a response to a previous request.
        :param message: the message to be examined
        :returns True: if and only if `message` represents an unsolicited event notification from the server
        """
        pass

    @abstractmethod
    def is_success(self, response: dict):
        """
        Examines the contents of the given response to a prior request, in order to determine whether the
        responses represents a successful outcome or an error. This method will be invoked only for those
        messages for which the `is_event` method returns False.
        :param response: the response to be examined
        :returns True: if and only if `response` represents a successful outcome to the corresponding request
        """
        pass

    def _handle_response(self, response):
        with self._lock:
            on_success, on_error = self._pending_requests.pop(0)
        if self.is_success(response) and on_success:
            on_success(response)
        elif on_error:
            on_error(response)

    def _run(self):
        message_text = None
        while not self._shutdown.is_set():
            try:
                message_text = self._connection.recv(self.RECV_TIMEOUT_SECONDS)
                if message_text:
                    message = json.loads(message_text)
                    if self.is_event(message) and self.on_event:
                        self.on_event(message)
                    else:
                        self._handle_response(message)
            except KeyError as err:
                logger.error(f"error processing message: {err}: {message_text}", file=sys.stderr)
            except json.JSONDecodeError as err:
                logger.error(f"error decoding message: {err}: {message_text}", file=sys.stderr)
            except ConnectionClosed:
                break
        logger.debug("client shutdown")

    def send(self, message: dict, on_success=None, on_error=None):
        """
        Sends a request to the server for which a response is expected.
        :param message: the request message to send
        :param on_success: an optional callback that will be invoked when a success response is received
        :param on_error: an optional callback that will be invoked when an error response is received
        """
        message_text = json.dumps(message)
        with self._lock:
            self._connection.send(message_text)
            self._pending_requests.append((on_success, on_error))

    def start(self):
        """ Opens the connection to the server and starts the service thread for receiving server messages """
        self._connection.open()
        self._thread.start()
        logger.debug("client started")

    def stop(self):
        """ Closes the connection to the server and stops the service thread for receiving server messages """
        self._connection.close()
        self._shutdown.set()
        self._thread.join()
        logger.debug("client stopped")
