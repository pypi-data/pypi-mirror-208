import logging
import time
from threading import Thread
from typing import Callable, Dict

from websockets.sync.server import serve as ws_serve, ServerConnection, WebSocketServer
from websockets.http11 import Response as WsResponse

from .game_connection import GameConnection, WsGameConnection

logger = logging.getLogger(__name__)


class WsGameListener:

    def __init__(self, local_ip: str, local_port: int,
                 on_connection: Callable[[GameConnection], None],
                 on_authenticate: Callable[[str, str], Dict] = None,
                 on_stop: Callable[[], None] = None):
        """
        Creates a new WebSocket listener.
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
        self.on_authenticate = on_authenticate
        self.on_connection = on_connection
        self.on_stop = on_stop
        self._thread = Thread(target=self._run)
        self._server: WebSocketServer = None

    def _handle_connection(self, ws_conn: ServerConnection):
        connection = WsGameConnection(ws_conn)
        self.on_connection(connection)

    def _unauthorized_response(self, reason: str) :
        logger.error(f"authentication failed: {reason}")
        return WsResponse(401, "Unauthorized", {})

    def _bad_request_response(self, reason):
        logger.error(f"authentication failed: {reason}")
        return WsResponse(400, "Bad request", {})

    def _skip_authentication(self, ws_conn: ServerConnection, request):
        request.claims = None

    def _handle_authentication(self, ws_conn: ServerConnection, request):
        gid = request.path.split("/")[-1]
        if not gid:
            return self._bad_request_response("no gid")

        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return self._unauthorized_response("invalid authorization header value")

        i = auth.index(" ")
        while auth[i] == " ":
            i += 1

        token = auth[i:]
        if not token:
            return self._unauthorized_response("token not present")

        claims = self.on_authenticate(gid, token)
        if not claims:
            return self._unauthorized_response("token not valid")

        request.claims = claims
        logger.debug("authentication successful")

    def _run(self):
        process_request = self._handle_authentication if self.on_authenticate else self._skip_authentication
        with ws_serve(self._handle_connection, self.local_ip, self.local_port,
                      process_request=process_request) as server:
            self._server = server
            server.serve_forever()

    def start(self):
        self._thread.start()
        logger.debug(f"ws server listening on {self.local_ip}:{self.local_port}")

    def stop(self):
        self._server.shutdown()
        self._thread.join()
        if self.on_stop:
            self.on_stop()
        logger.debug(f"ws server stopped")

    def run(self):
        self.start()
        done = False
        while not done:
            try:
                time.sleep(0.250)
            except KeyboardInterrupt:
                done = True
        self.stop()