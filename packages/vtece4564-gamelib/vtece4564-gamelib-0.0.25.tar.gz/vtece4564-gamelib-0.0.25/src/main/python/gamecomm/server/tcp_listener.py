import logging
import selectors
import socket
import time
from threading import Thread, Event
from typing import Callable, Dict

from .game_connection import GameConnection, TcpGameConnection

logger = logging.getLogger(__name__)


class TcpGameListener:

    SELECT_TIMEOUT = 0.250

    def __init__(self, local_ip: str, local_port: int,
                 on_connection: Callable[[GameConnection], None],
                 on_authenticate: Callable[[str, str], Dict] = None,
                 on_stop: Callable[[], None] = None):
        """
        Creates a new TCP listener.
        :param local_ip: local IP address identifying the interface on which to accept connections
            (usually an empty string)
        :param local_port: the local IP port to which the listener's socket will be bound
        :param on_connection: a callback function that will be invoked for each new client connection
        :param on_authenticate: a optional callback function that will authenticate a client's presented game ID
            and authentication token before the client is admitted (via the `on_connection` callback)
        :param on_stop: an optional callback function that will be invoked when the `stop` method is invoked
            on the listener (after the listener's service thread has been stopped and the listening is closed)
        """
        self.local_ip = local_ip
        self.local_port = local_port
        self.on_connection = on_connection
        self.on_authenticate = on_authenticate
        self.on_stop = on_stop
        self._thread = Thread(target=self._run)
        self._shutdown = Event()
        self._listener_socket: socket.socket = None
        self._selector = selectors.DefaultSelector()

    def _open_listener(self):
        try:
            self._listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._listener_socket.bind((self.local_ip, self.local_port))
            self._listener_socket.listen()
            self._selector.register(self._listener_socket, selectors.EVENT_READ)
        except OSError as err:
            logger.error(f"cannot listen on {self.local_ip}:{self.local_port}: {err}")

    def _handle_connection(self):
        try:
            stream_socket, peer_address = self._listener_socket.accept()
            connection = TcpGameConnection(stream_socket, peer_address)
            if self.on_authenticate:
                connection.handshake(self.on_authenticate)
            thread = Thread(target=self.on_connection, args=(connection,), daemon=True)
            thread.start()
        except OSError as err:
            logger.error(f"error accepting new connection: {err}")

    def _run(self):
        while not self._shutdown.is_set():
            if self._selector.select(self.SELECT_TIMEOUT):
                self._handle_connection()

    def start(self):
        self._open_listener()
        self._thread.start()
        logger.debug(f"tcp server listening on {self.local_ip}:{self.local_port}")

    def stop(self):
        self._shutdown.set()
        self._thread.join()
        if self.on_stop:
            self.on_stop()
        logger.debug(f"tcp server stopped")

    def run(self):
        self.start()
        done = False
        while not done:
            try:
                time.sleep(0.250)
            except KeyboardInterrupt:
                done = True
        self.stop()