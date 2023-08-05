import hashlib
import json
import os
import sys
import unittest

from dsframework.base.server.cache.cache import Cache, CacheItem
from dsframework.base.server.cache.cache_utils import CacheProvider, DoNothingCache, InMemoryCache, CacheFacade, \
    Compression, KeyTransformer
from dsframework.base.server.cache.redis_cache import RedisCache


class TestCacheProvider(unittest.TestCase):
    def test_get_cache_none(self):
        cache = CacheProvider.get_cache(Cache.Type.NONE)
        self.assertIsInstance(cache, DoNothingCache)

    def test_get_cache_redis(self):
        cache = CacheProvider.get_cache(Cache.Type.REDIS)
        self.assertIsInstance(cache, RedisCache)

    def test_get_cache_in_memory(self):
        cache = CacheProvider.get_cache(Cache.Type.IN_MEMORY)
        self.assertIsInstance(cache, InMemoryCache)

    def test_get_cache_invalid_type(self):
        with self.assertRaises(AttributeError):
            CacheProvider.get_cache("InvalidType")


class TestCacheFacade(unittest.TestCase):
    def setUp(self):
        self.mock_cache = InMemoryCache()

    def test_set_get(self):
        # Test with full cache hit
        input_ = [{"key": "value1"}, {"key": "value2"}]
        self.cache_facade = CacheFacade(self.mock_cache, Cache.Type.IN_MEMORY,
                                        input_, "test_host", "test_service_account")
        self.cache_facade.get("key")
        self.cache_facade.set(input_)
        result = self.cache_facade.get("key")
        self.assertEqual(result, input_)

        # Test with partial cache hit should return empty
        partial_input = [{"key": "value1"}, {"key": "value_not_in_cache"}]
        self.cache_facade = CacheFacade(self.mock_cache, Cache.Type.IN_MEMORY,
                                        partial_input, "test_host", "test_service_account")
        result = self.cache_facade.get("key")
        self.assertEqual([], result)


class TestCompression(unittest.TestCase):
    def test_pack_predictable(self):
        value = [1, 2, 3]
        packed_value = Compression.pack_predictable(value)

        # Ensure that the packed value is not the same as the original value
        self.assertNotEqual(packed_value, value)

        # Ensure that the packed value can be decompressed and loaded correctly
        self.assertEqual(Compression.unpack_predictable(packed_value), value)


class TestKeyTransformer(unittest.TestCase):

    def test_serialize(self):
        key = {'a': 1, 'b': 2}
        key_transformer = KeyTransformer()
        serialized_key = key_transformer._serialize(key)

        # Ensure that the serialized key is a JSON string
        self.assertIsInstance(serialized_key, str)
        try:
            json.loads(serialized_key)
        except ValueError:
            self.fail('_serialize did not produce a proper JSON as expected')

        # Ensure that the serialized key is not the same as the original key
        self.assertNotEqual(serialized_key, key)

    def test_build_key_string(self):
        key = 'key'
        service_name = 'service'
        git_tag_version = 'v1.0'
        os.environ['GAE_SERVICE'] = service_name
        os.environ['DD_VERSION'] = git_tag_version
        key_transformer = KeyTransformer()
        built_key_string = key_transformer._build_key_string(key)

        # Ensure that the built key string is the correct format
        self.assertEqual(built_key_string, f'{service_name}_{git_tag_version}_{key}')

    def test_encode(self):
        key = 'key'
        key_transformer = KeyTransformer()
        encoded_key = key_transformer._encode(key)

        # Ensure that the encoded key is a bytes object
        self.assertEquals(encoded_key, key.encode('utf-8', 'replace'))

    def test_hash(self):
        key = b'key'
        key_transformer = KeyTransformer()
        hashed_key = key_transformer._hash(key)

        # Ensure that the hashed key is a string
        self.assertEquals(hashed_key, hashlib.sha256(key).hexdigest())
