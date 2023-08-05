import unittest

from dsframework.base.server.cache.cache import CacheItem, Cache


class TestCacheItem(unittest.TestCase):
    def test_cache_item(self):
        cache_item = CacheItem("test_key", "test_value")
        self.assertEqual(cache_item.key, "test_key")
        self.assertEqual(cache_item.value, "test_value")


class TestCache(unittest.TestCase):
    def test_cache_abstract_methods(self):
        cache = Cache()
        with self.assertRaises(NotImplementedError):
            cache.get([])
        with self.assertRaises(NotImplementedError):
            cache.set([])
        with self.assertRaises(NotImplementedError):
            cache.status()
