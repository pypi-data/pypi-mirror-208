"""Test the clean-up functionality of the cache(s)"""
import logging
import configparser
import unittest
import datetime
import tempfile
from pathlib import Path

from metaindex import logger
from metaindex import cache
from metaindex import configuration
from metaindex import indexers as _
from metaindex import CacheEntry


class NoCacheBackend:
    """A fake cache backend providing the API but nothing else"""
    def __init__(self):
        self.is_started = True

    def find(self, *_):
        return []

    def get(self, *_):
        return []

    def rename(self, *_):
        pass

    def insert(self, *_):
        pass

    def forget(self, *_):
        pass

    def refresh(self, *_):
        pass

    def cleanup(self, *_):
        pass

    def last_modified(self):
        return datetime.datetime.min

    def keys(self, *_):
        return set()

    def start(self):
        pass

    def quit(self):
        pass


class TestCacheBase(unittest.TestCase):
    """Base class for all test cases"""

    def setUp(self):
        conf = configparser.ConfigParser(interpolation=None)
        conf.read_dict(configuration.CONF_DEFAULTS)

        general = conf[configuration.SECTION_GENERAL]
        general[configuration.CONFIG_CACHE] = ':memory:'
        general[configuration.CONFIG_INDEX_UNKNOWN] = 'yes'

        logger.setup(logging.ERROR)

        self.config = configuration.Configuration(conf)
        self.cache = self.cache_setup()
        self.tmppath = tempfile.TemporaryDirectory()
        self.path = Path(self.tmppath.name)

        if self.cache is None:
            return

        self.cache.insert(CacheEntry(self.path / 'a.txt',
                                     [('identifier', 'a')],
                                     datetime.datetime.now()))
        (self.path / "sub").mkdir()
        (self.path / "sub" / "file.md").write_text("Content")
        self.cache.insert(CacheEntry(self.path / "sub" / "file.md",
                                     [('title', 'file')],
                                     datetime.datetime.now()))
        self.cache.insert(CacheEntry(self.path / "sub" / "gone.jpg",
                                     [('type', 'image')],
                                     datetime.datetime.now()))
        self.cache.insert(CacheEntry(self.path / "sub" / "further" / "nope.txt",
                                     [('tag', 'foo')],
                                     datetime.datetime.now()))

    def tearDown(self):
        self.tmppath.cleanup()

    def cache_setup(self):
        self.skipTest("Base class")
        return None

    def test_base_setup(self):
        results = list(self.cache.find(''))

        self.assertEqual(len(results), 4)

    def test_clean_up_all(self):
        self.cache.cleanup()
        results = list(self.cache.find(''))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].path, self.path / "sub" / "file.md")

    def test_clean_up_further(self):
        self.cache.cleanup([self.path / "sub" / "further"])
        results = list(self.cache.find(''))

        self.assertEqual(len(results), 3)
        self.assertEqual(len(self.cache.find('tag:foo')), 0)

    def test_clean_up_sub(self):
        self.cache.cleanup([self.path / "sub"])
        results = list(self.cache.find(''))

        self.assertEqual(len(results), 2)
        self.assertEqual(len(self.cache.find('type:image')), 0)


class TestCache(TestCacheBase):
    """The tests for the base Cache"""

    def cache_setup(self):
        return cache.Cache(self.config)


class TestMemoryCache(TestCacheBase):
    """The tests for the MemoryCache"""

    def cache_setup(self):
        memcache = cache.MemoryCache(self.config)
        memcache.tcache = NoCacheBackend()
        memcache.start()
        memcache.wait_for_reload()
        return memcache

    def tearDown(self):
        super().tearDown()
        self.cache.quit()
