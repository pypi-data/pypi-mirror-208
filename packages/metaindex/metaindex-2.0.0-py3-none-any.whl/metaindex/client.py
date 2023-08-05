"""The client interface to the metaindex server"""
import socket

from metaindex import configuration
from metaindex import proto
from metaindex import logger


class DisconnectedError(RuntimeError):
    """The connection was disconnected from the server side"""


class Client:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def reconnect(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connection.connect(str(self.config.path(configuration.SECTION_GENERAL,
                                                     configuration.CONFIG_SOCKET)))

    def connection_ok(self):
        """Check whether the connection to the server is working

        Returns ``True`` if the connection works, otherwise ``False``
        """
        try:
            self.ensure_connection()
            return True
        except (OSError, DisconnectedError):
            del self.connection
            self.connection = None
            return False

    def ensure_connection(self):
        if self.connection is None:
            self.reconnect()

        self.send(proto.Ping())
        pong = self.recv()

    def send(self, msg):
        assert isinstance(msg, proto.Message)
        if self.connection is None:
            self.reconnect()

        assert self.connection is not None
        self.connection.send(bytes(msg.serialize(), 'utf-8'))

    def recv(self):
        assert self.connection is not None

        req = ''
        while True:
            req += str(self.connection.recv(4096), 'utf-8')

            if len(req) == 0:
                raise DisconnectedError()

            try:
                msg = proto.Message.deserialize(req)
                return msg
            except proto.MessageParseError as exc:
                logger.debug("Not (yet?) valid request '%s': %s", req, exc)
