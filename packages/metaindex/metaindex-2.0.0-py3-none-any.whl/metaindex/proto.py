"""The protocol between metaindex server and client

Each message can be serialised and deserialised using JSON and sent
over the socket or received from a socket.
"""
import json
from pathlib import Path

from metaindex.cacheentry import CacheEntry
from metaindex.shared import jsonify


class MessageParseError(RuntimeError):
    pass


class InvalidMessageError(RuntimeError):
    pass


class MessageStructureError(RuntimeError):
    pass


class Message:
    def __init__(self, msg=None):
        self.msg = msg or dict()

    def copy(self):
        return type(self)(self.msg)

    @classmethod
    def deserialize(cls, text):
        try:
            msg = json.loads(text)
        except json.JSONDecodeError as exc:
            raise MessageParseError(str(exc))

        if not isinstance(msg, dict):
            raise MessageStructureError(f"Not a dictionary: {text}")

        if msg.get('status', None) == 'ok':
            if 'r' in msg:
                return QueryResult(msg)
            if 'synonyms' in msg:
                return Config(msg)
            return OkayResponse(msg)

        if msg.get('status', None) == 'err':
            return ErrorResponse(msg)

        if msg.get('status', None) == 'pong':
            return Pong(msg)

        if msg.get('cmd', None) == 'ping':
            return Ping(msg)

        if msg.get('cmd', None) == 'update':
            return Update(msg)

        if msg.get('cmd', None) == 'query':
            return Query(msg)

        if msg.get('cmd', None) == 'get':
            return GetMetadata(msg)

        if msg.get('cmd', None) == 'clear':
            return Clear(msg)

        if msg.get('cmd', None) == 'forget':
            return Forget(msg)

        if msg.get('cmd', None) == 'compact':
            return Compact(msg)

        if msg.get('cmd', None) == 'mrecent':
            return GetMostRecent(msg)

        if msg.get('cmd', None) == 'shutdown':
            return Shutdown(msg)

        if msg.get('cmd', None) == 'config':
            return GetConfig(msg)

        raise InvalidMessageError(f"Unknown message type: {text}")

    def serialize(self):
        """Returns the string of this object in JSON encoding"""
        return json.dumps(self.do_serialize())

    def do_serialize(self):
        raise NotImplementedError()

    def __str__(self):
        return str(self.serialize())


class Response(Message):
    def __bool__(self):
        return self.ok()

    def ok(self):
        """Whether or not the response is positive"""
        raise NotImplementedError()


class OkayResponse(Response):
    """Indicates that a command or request was acknowledged"""
    def do_serialize(self):
        return {"status": "ok"}

    def ok(self):
        return True


class ErrorResponse(Response):
    """Indicates that a command failed

    A reason might be available"""
    def __init__(self, msg=None, reason=None):
        super().__init__(msg)

        self.reason = reason
        if msg is not None:
            self.reason = msg.get('reason', reason)

    def copy(self):
        that = super().copy()
        that.reason = self.reason
        return that

    def do_serialize(self):
        msg = {"status": "err"}
        if self.reason is not None:
            msg['reason'] = self.reason
        return msg

    def ok(self):
        return False


class Ping(Message):
    """A simple ping to check the connection"""
    def do_serialize(self):
        return {"cmd": "ping"}


class Pong(Response):
    """A response to ping"""
    def do_serialize(self):
        return {"status": "pong"}

    def ok(self):
        return True


class Shutdown(Message):
    """Request the server shut down"""
    def do_serialize(self):
        return {"cmd": "shutdown"}


class Clear(Message):
    """Command to clear the cache"""
    def do_serialize(self):
        return {"cmd": "clear"}


class GetConfig(Message):
    """Request metadata configuration from the server"""
    def do_serialize(self):
        return {"cmd": "config"}


class Config(Response):
    """Metadata configuration"""
    def __init__(self, msg=None, config=None):
        super().__init__(msg)
        self.synonyms = {}
        self.synonymized = {}

        if msg is not None:
            self.synonyms = msg.get('synonyms', {})
            self.synonymized = msg.get('synonymized', {})
        if config is not None:
            self.synonyms = {k: jsonify(v) for k, v in config.synonyms.items()}
            self.synonymized = {k: jsonify(v) for k, v in config.synonymized.items()}

    def do_serialize(self):
        return {"status": "ok",
                "synonyms": self.synonyms,
                "synonymized": self.synonymized}

    def ok(self):
        return True


class PathsMessage(Message):
    """An abstract message that sends paths to the server"""

    REQUEST = None

    def __init__(self, msg=None, paths=None):
        super().__init__(msg)
        self.paths = paths or []

        if msg is not None:
            self.paths = [Path(p) for p in msg['paths']]

    def copy(self):
        that = super().copy()
        that.paths = self.paths[:]
        return that

    def do_serialize(self):
        if self.REQUEST is None:
            raise NotImplementedError()

        msg = {'cmd': self.REQUEST,
               'paths': [str(p) for p in self.paths]}
        return msg


class Forget(PathsMessage):
    """Remove these paths from the database

    Similar to 'clear', but more selective
    """
    REQUEST = 'forget'


class Compact(Message):
    """Compacting the database"""
    def do_serialize(self):
        return {"cmd": "compact"}


class Update(Message):
    """Command to update a document's metadata"""
    def __init__(self, msg=None, entries=None):
        super().__init__(msg)
        self.entries = []
        if entries is not None:
            self.entries = entries

        if msg is not None:
            self.entries = [CacheEntry.from_dict(part)
                            for part in msg['entries']]

    def copy(self):
        that = super().copy()
        that.entries = [e.copy() for e in self.entries]
        return that

    def do_serialize(self):
        msg = {'cmd': 'update',
               'entries': [e.as_dict() for e in self.entries]}
        return msg


class Query(Message):
    """A query to retrieve a list of documents"""
    def __init__(self, msg=None, query=None):
        super().__init__(msg)
        self.query = query

        if msg is not None:
            self.query = msg['q']

    def copy(self):
        that = super().copy()
        that.query = self.query
        return that

    def do_serialize(self):
        msg = {'cmd': 'query',
               'q': self.query}
        return msg


class QueryResult(Response):
    """Result of a query"""
    def __init__(self, msg=None, results=None):
        super().__init__(msg)
        self.results = []
        self.status = None

        if results is not None:
            self.results = results

        if msg is not None:
            self.results = msg['r'][:]
            self.status = msg['status']

    def entries(self):
        """Iterate through the results in the form of CacheEntries"""
        for _, result in self.results:
            yield CacheEntry.from_dict(result)

    def copy(self):
        that = super().copy()
        that.results = [r.copy() for r in self.results]
        return that

    def ok(self):
        return self.status == 'ok'

    def do_serialize(self):
        msg = {'status': 'ok',
               'r': self.results}
        return msg


class GetMetadata(PathsMessage):
    """Get all metadata for the given paths"""
    REQUEST = 'get'
    def __init__(self, msg=None, paths=None, tags=None):
        super().__init__(msg, paths)
        self.selected_tags = tags

        if msg is not None:
            self.selected_tags = msg.get('tags', None)

    def do_serialize(self):
        data = super().do_serialize()
        data['tags'] = self.selected_tags
        return data


class GetMostRecent(Message):
    """Get the most recent entry"""
    def do_serialize(self):
        return {'cmd': 'mrecent'}
