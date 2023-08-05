import datetime
import pathlib
import queue
import threading

from metaindex import indexer
from metaindex import configuration
from metaindex import stores
from metaindex import shared
from metaindex import logger
from metaindex import proto
from metaindex.cacheentry import CacheEntry
from metaindex.client import Client, DisconnectedError


class CacheBase:
    """The basic Cache API"""
    def __init__(self, config=None):
        self.config = config or configuration.load()
        assert isinstance(self.config, configuration.Configuration)
        self.is_initialized = False

    def refresh(self, paths=None, recursive=True, processes=None, callback=None, storage=None):
        """(Re-)Index all items found in the given paths or all cached items
           if paths is ``None``.

        If any item in the list is a directory and recursive is True, all
        items inside that directory (including any all subdirectories) will
        be indexed, too.

        processes may be set to a number of processes that will be used in
        parallel to index the files. If left at None, there will be as many
        processes launched as CPUs are available.

        ``callback`` may be a function that accepts one parameter: the CacheEntry
        instance of a newly indexed document. When indexing many files, this
        callback will be called per file, if it's not ``None``.

        ``storage`` is the human-readable (and human-provided) label for the storage
        that the files are residing on'
        """
        raise NotImplementedError()

    def cleanup(self, paths=None):
        """Find and remove all entries in the cache that refer to no longer existing files

        If ``paths`` is provided, only clean up missing files that are inside these paths"""
        raise NotImplementedError()

    def clear(self):
        """Remove everything from the cache"""
        raise NotImplementedError()

    def forget(self, paths):
        """Remove all ``paths`` from the cache.

        :param paths: The list of paths to remove from cache."""
        raise NotImplementedError()

    def expire_metadata(self, paths):
        """Remove all metadata associated to these paths

        But keep the paths in the database.
        """
        raise NotImplementedError()

    def find(self, query):
        """Find all items matching this query.

        query may either be a human-written search term or a Query instance.

        Returns a list of (path to file, metadata, last_modified) tuples.
        """
        raise NotImplementedError()

    def get(self, paths):
        """Get metadata for all items of paths

        paths may also be a single path instead of a list of paths.

        If any element of paths is pointing to a directory and recursive is
        set to True, get will return the metadata for all elements inside
        that directory (and their subdirectories'), too.
        """
        raise NotImplementedError()

    def keys(self):
        """Get all metadata keys

        :rtype: ``list[str]``
        """
        raise NotImplementedError()

    def rename(self, path, new_path, is_dir=None):
        """Rename all entries in the database that are 'path' to 'new_path'

        If 'path' is pointing to a directory, all files in the subdirectories
        will be renamed correctly, too.
        That means that this operation can affect many rows and take some time.

        If you already renamed path to new_path, you have to provide the `is_dir`
        parameter to indicate whether the item you renamed is a directory or not!
        """
        raise NotImplementedError()

    def last_modified(self):
        """Return the date and time of the entry that most recently updated in the database.
        :rtype: ``datetime.datetime``
        """
        raise NotImplementedError()

    def insert(self, item):
        """Insert the CacheEntry ``entry`` into the cache.

        This operation will not modify the item in the filesystem nor update
        any other form of metadata persistency for the item.
        This function really only affects the cache.
        """
        raise NotImplementedError()

    def parse_extra_metadata(self, metafile):
        """Extract extra metadata from this file"""
        data = stores.get_for_collection(metafile)

        for filename in data.keys():
            data[filename][shared.IS_RECURSIVE] = data[filename][shared.IS_RECURSIVE] and \
                                                  self.config.recursive_extra_metadata

        return data


class XapianClientCache(CacheBase):
    """A Cache-interface that connects to the local xapian server backend"""
    def __init__(self, config=None):
        super().__init__(config)
        self.client = Client(self.config)
        try:
            self.reconnect()
        except (OSError, DisconnectedError):
            pass

    def connection_ok(self):
        return self.client.connection_ok()

    def reconnect(self):
        self.client.reconnect()
        self.is_initialized = True

        self.client.send(proto.GetConfig())
        response = self.client.recv()
        if bool(response):
            self.config.synonyms = response.synonyms.copy()
            self.config.synonymized = response.synonymized.copy()

    def compact(self):
        self.client.ensure_connection()
        self.client.send(proto.Compact())
        response = self.client.recv()
        return bool(response)

    def find(self, query):
        self.client.ensure_connection()
        self.client.send(proto.Query(query=query))
        response = self.client.recv()
        if response:
            return list(response.entries())
        return []

    def get(self, paths, tags=None):
        if paths is None:
            return []

        if isinstance(paths, (set, tuple)):
            paths = list(paths)

        if not isinstance(paths, list):
            paths = [paths]

        if len(paths) == 0:
            return []

        paths = [str(shared.make_mount_relative(p))
                 for p in paths]

        self.client.ensure_connection()
        self.client.send(proto.GetMetadata(paths=paths, tags=tags))
        response = self.client.recv()
        if response:
            return list(response.entries())
        return []

    def keys(self):
        raise NotImplementedError()

    def refresh(self, paths=None, recursive=True, processes=None, callback=None, storage=None):
        if paths is None:
            return []

        if isinstance(paths, (set, tuple)):
            paths = list(paths)

        if not isinstance(paths, list):
            paths = [paths]

        if len(paths) == 0:
            return []

        files = self.config.find_indexable_files(paths, recursive)

        # cache of last_modified dates for files
        last_modified = {fn: shared.get_last_modified(fn) for fn in files}

        # obtain cached metadata
        last_cached = {entry.path: entry for entry in self.get(files, ['last_modified'])}

        # filter out files that haven't changed
        files = [f for f in files
                 if f not in last_cached or f not in last_modified
                    or last_modified[f] > last_cached[f].last_modified
                    or any(shared.get_last_modified(s) > last_cached[f].last_modified
                           for s, _ in self.config.find_all_sidecar_files(f))]

        generator = indexer.index_files(files,
                                        self.config,
                                        processes,
                                        self.config.ocr,
                                        self.config.extract_fulltext,
                                        last_modified,
                                        last_cached)

        results = []
        for result in generator:
            if not result.success and not self.config.index_unknown:
                continue

            try:
                result.info.last_modified = last_modified[result.filename]
                indexed = self.reduce(result.info)
                indexed.rel_path = shared.make_mount_relative(indexed.path)
                indexed.storage_label = storage
                results.append(indexed)

                self.client.ensure_connection()
                self.client.send(proto.Update(entries=[indexed]))
                response = self.client.recv()
                if not response:
                    logger.error("Failed to update database: %s", response.reason)
                    break

                if callback is not None:
                    callback(indexed)
            except KeyboardInterrupt:
                break

        return results

    def insert(self, item):
        self.client.ensure_connection()
        self.client.send(proto.Update(entries=[self.reduce(item)]))
        self.client.recv()

    def rename(self, path, new_path, is_dir=None):
        raise NotImplementedError()

    def last_modified(self):
        self.client.ensure_connection()
        self.client.send(proto.GetMostRecent())
        results = self.client.recv()
        if results:
            results = list(results.entries())
            if len(results) > 0:
                return results[0].last_modified
        return datetime.datetime.min

    def cleanup(self, paths=None):
        raise NotImplementedError()

    def clear(self):
        self.client.ensure_connection()
        self.client.send(proto.Clear())
        self.client.recv()

    def forget(self, paths):
        self.client.ensure_connection()
        self.client.send(proto.Forget(paths=[str(p) for p in paths]))
        self.client.recv()

    def expire_metadata(self, paths):
        if paths is None:
            return
        elif not isinstance(paths, list):
            paths = [paths]

        if isinstance(paths, list):
            paths = [pathlib.Path(path).resolve()
                     for path in paths]
        entries = [CacheEntry(p) for p in paths]

        self.client.ensure_connection()
        self.client.send(proto.Update(entries=entries))
        self.client.recv()

    def reduce(self, entry):
        """Reduces the tags in ``CacheEntry`` ``entry`` in place

        Modifications are done in place to ``entry``, but for convenience, ``entry`` is
        also returned.

        It removes all metadata fields that are not in the synonyms.
        """
        for key in set(entry.metadata.keys()):
            if key in self.config.synonymized:
                entry.metadata[key] = list(set(entry.metadata[key]))
            else:
                del entry.metadata[key]

        return entry


class ThreadedCache(CacheBase):
    """Special version of Cache to be used in multi-threaded applications

    To use this, create an instance and execute ``start``.
    """
    GET = "get"
    FIND = "find"
    REFRESH = "refresh"
    INSERT = "insert"
    GET_KEYS = "get-keys"
    RENAME = "rename"
    FORGET = "forget"
    CLEAR = "clear"
    CLEANUP = "cleanup"
    LAST_MODIFIED = "last_modified"
    EXPIRE = "expire"

    BACKEND_TYPE = XapianClientCache

    def __init__(self, config):
        super().__init__(config)
        self.queue = queue.Queue()
        self._quit = False
        self.handler = threading.Thread(target=self.handler_loop)
        self.results = queue.Queue()
        self.single_call = threading.Lock()
        self.cache = None
        self._started = False

    @property
    def is_started(self):
        """Whether or not the thread has been started"""
        return self._started

    def assert_started(self):
        """Ensure that the worker thread has been started"""
        if not self._started:
            raise RuntimeError("Not started")

    def get(self, paths):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.GET, paths))
            return self.results.get()

    def find(self, query):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.FIND, query))
            return self.results.get()

    def refresh(self, paths=None, recursive=True, processes=None, callback=None, storage=None):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.REFRESH, paths, recursive, processes, storage))
            return self.results.get()

    def insert(self, item):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.INSERT, item))
            return self.results.get()

    def rename(self, path, new_path, is_dir=None):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.RENAME, path, new_path, is_dir))
            return self.results.get()

    def forget(self, paths):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.FORGET, paths))
            return self.results.get()

    def clear(self):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.CLEAR,))
            return self.results.get()

    def cleanup(self, paths=None):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.CLEANUP, paths))
            return self.results.get()

    def expire_metadata(self, paths):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.EXPIRE, paths))
            return self.results.get()

    def keys(self):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.GET_KEYS,))
            return self.results.get()

    def last_modified(self):
        self.assert_started()
        with self.single_call:
            self.queue.put((self.LAST_MODIFIED,))
            return self.results.get()

    def start(self):
        """Launch the cache thread"""
        self.handler.start()

    def quit(self):
        """End the cache thread"""
        self._quit = True
        if self._started:
            self._started = False
            self.queue.put("")
            self.handler.join()

    def handler_loop(self):
        """The handler running in the separate thread.

        You do not need to call this. Call ``start`` instead.
        """
        if self._started:
            return
        self.cache = type(self).BACKEND_TYPE(self.config)
        self._started = True
        while not self._quit:
            item = self.queue.get()
            if len(item) < 1:
                continue

            command = item[0]
            args = item[1:]
            result = None

            try:
                if command == self.GET:
                    result = self.cache.get(*args)
                elif command == self.FIND:
                    result = self.cache.find(*args)
                elif command == self.REFRESH:
                    result = self.cache.refresh(*args)
                elif command == self.INSERT:
                    self.cache.insert(*args)
                elif command == self.LAST_MODIFIED:
                    result = self.cache.last_modified()
                elif command == self.GET_KEYS:
                    result = self.cache.keys()
                elif command == self.FORGET:
                    self.cache.forget(*args)
                elif command == self.CLEAR:
                    self.cache.clear()
                elif command == self.CLEANUP:
                    self.cache.cleanup(*args)
                elif command == self.EXPIRE:
                    self.cache.expire_metadata(*args)
            except Exception as exc:
                result = exc

            self.results.put(result)


Cache = XapianClientCache


if __name__ == '__main__':
    logger.setup('DEBUG')
    cache = Cache()
    breakpoint()
