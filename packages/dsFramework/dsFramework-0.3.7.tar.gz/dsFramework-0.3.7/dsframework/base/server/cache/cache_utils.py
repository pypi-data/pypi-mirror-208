import collections
import os
import logging
import pickle
import sys
import zlib
import ujson
import hashlib
from typing import Any, List, Union, Dict
from pydantic import BaseModel
from dsframework.base.server.cache.cache import Cache, CacheItem
from dsframework.base.server.cache.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class KeyTransformer:
    """!Class for transforming cache keys by applying Serialization, Encoding and Hashing by default.
    Inherit and override the transform method to provide a custom transformation implementation.

    Attributes:
        git_tag_version: the git tag of this instance (taken from environment variable 'DD_VERSION')
        service_name: the service name (taken from environment variable 'GAE_SERVICE')
    """

    def __init__(self):
        self.git_tag_version = os.environ.get('DD_VERSION', '')
        self.service_name = os.environ.get('GAE_SERVICE', 'local')

    @staticmethod
    def _serialize(key: dict) -> str:
        """!Returns a JSON serialized key"""
        return ujson.dumps(key, ensure_ascii=False)

    def _build_key_string(self, key: str) -> str:
        """!Returns the key prefixed by the service name and tag version"""
        return f'{self.service_name}_{self.git_tag_version}_{key}'

    @staticmethod
    def _encode(key: str) -> bytes:
        """!Returns a UTF-8 encoded key"""
        return key.encode('utf-8', 'replace')

    @staticmethod
    def _hash(key: bytes):
        """!Returns a SHA256 hashed key"""
        return hashlib.sha256(key).hexdigest()

    def transform(self, key: dict) -> str:
        """!Transforms a given key using a set of pre-defined functions:
        JSON Serialization, UTF-8 Encoding and SHA256 hashing.

        :param key: the key dictionary to transform
        :return: the transformed key string
        """

        result = self._serialize(key)
        result = self._build_key_string(result)
        result = self._encode(result)
        result = self._hash(result)
        return result


class Compression:
    """!Utility class for compressing/decompression values. Applies pickle serialization.
    Inherit this class and override its methods to supply a different compression implementation for the Cache.
    """

    @staticmethod
    def pack_predictable(value):
        """!Pickle dumps + zlib compress (pickle protocol no. 5 for stability)"""
        unzipped = pickle.dumps(value, protocol=5)
        return zlib.compress(unzipped)

    @staticmethod
    def unpack_predictable(value):
        """!Zlib decompress + pickle loads."""
        unzipped = zlib.decompress(value)
        return pickle.loads(unzipped)


default_key_transformer = KeyTransformer()
default_compression = Compression()


class CacheFacade:
    """!Class to encapsulate all the necessities around the basic cache functionalities.
    Saves keys internally on get() to be used later on the set().

    Attributes:
        cache: the actual cache instance
        cache_type: the cache type (enum)
        data: the request data
        host: the host name to be used in logs
        service_account: the service account to be used in logs
        key_transformer: in charge of key transformations (serialization, encoding, hashing by default)
        with_compression: enable/disable value compression (disabled by default)
        compression: compression implementation (pickle + zlib by default)
    """
    def __init__(self, cache: Cache, cache_type: Cache.Type,
                 key_transformer: KeyTransformer = default_key_transformer,
                 with_compression: bool = False, compression: Compression = default_compression) -> None:
        super().__init__()
        self.__cache = cache
        self.__cache_type = cache_type
        self.__data = None
        self.__host = None
        self.__service_account = None
        self.__key_transformer = key_transformer
        self.__compression = compression
        self.__with_compression = with_compression
        self.__cache_keys = None

        # Define the "get" and "set" functions once, so no if statements are needed for every request
        if cache_type is Cache.Type.NONE:
            self.get = self.__cache.get
            self.set = self.__cache.set
        else:
            self.get = self.facade_get
            self.set = self.facade_set

    def get_request_data(self, data, host, service_account) -> None:
        self.__data = data
        self.__host = host
        self.__service_account = service_account

    # noinspection PyBroadException
    def facade_get(self, cache_keys_search_keyword: str) -> List[Any]:
        """!Retrieves one or more items from the cache.
        Transforms each key using the default KeyTransformer or using the supplied one.
        If compression is enabled - decompress values using the default Compression or using the supplied one.

        :param cache_keys_search_keyword: keyword for locating values to be used as cache keys
        :return: a list of one or more items corresponding to the given list of keys
        """
        try:
            input_values = self._get_all_cache_keys_mapped_by_keyword(self.__data, cache_keys_search_keyword)
            # extract the list of signatures to be used as cache keys
            self.__cache_keys = [self.__key_transformer.transform(raw_key) for raw_key in input_values]
            outputs = self.__cache.get(self.__cache_keys)
            if self.all_values_not_none(outputs):
                outputs = [self._decompress_if(output) for output in outputs]
                return outputs
        except Exception:
            logger.exception("ERROR Failed retrieving items from Cache. Calling model instead. ",
                             extra=dict(input=self.__data, from_host=self.__host,
                                        from_service_account=self.__service_account))
        return []

    def _decompress_if(self, item):
        """!Decompress the given item if compression is enabled"""
        return self.__compression.unpack_predictable(item) if self.__with_compression else pickle.loads(item)

    def _get_all_cache_keys_mapped_by_keyword(self, collection: Union[List, Dict], keyword: str, depth: int = 0,
                                              max_depth: int = 10) -> List:
        """!Returns a list of values for the specified key in the collection.

        The function will recursively search through the collection and return a list
        of all values (cache keys) for the specified keyword. If the keyword is not found in the
        collection, the function will return an empty list. The search will stop when
        the maximum depth is reached.

        :param collection: (Union[List, Dict]) The collection to search.
        :param keyword: (str) The keyword to search for.
        :param depth: (int) The current depth of the search.
        :param max_depth: (int) The maximum depth of the search.

        :return: A list of values (cache keys) for the specified keyword.
        """
        values = []
        if depth > max_depth:
            return values
        if isinstance(collection, list):
            for item in collection:
                if isinstance(item, (list, dict)):
                    values.extend(self._get_all_cache_keys_mapped_by_keyword(item, keyword, depth + 1, max_depth))
        elif isinstance(collection, dict):
            if keyword in collection:
                values.append(collection[keyword])
            for value in collection.values():
                if isinstance(value, (list, dict)):
                    values.extend(self._get_all_cache_keys_mapped_by_keyword(value, keyword, depth + 1, max_depth))
        return values

    # noinspection PyBroadException
    def facade_set(self, output: List[BaseModel]) -> None:
        """!Stores one or more items in the cache.
        Transforms each key using the default KeyTransformer or using the supplied one.
        If compression is enabled - values are compressed using the default Compression or using the supplied one.

        :param output: the list of pipeline outputs to be stored
        """

        if len(self.__cache_keys) != len(output):
            # if the number of pipeline outputs is different from the number of keys - don't store the outputs at all
            return

        try:
            cache_items = []
            for i, cache_key in enumerate(self.__cache_keys):
                value = self._compress_if(output[i])
                cache_items.append(CacheItem(cache_key, value))
            self.__cache.set(cache_items)

        except Exception:
            logger.exception("ERROR Failed storing parsed signatures in Redis",
                             extra=dict(input=self.__data, output=output, from_host=self.__host,
                                        from_service_account=self.__service_account))

    def _compress_if(self, item):
        """!Compress the given item if compression is enabled"""
        return self.__compression.pack_predictable(item) if self.__with_compression else pickle.dumps(item)

    @staticmethod
    def all_values_not_none(cache_values: list) -> bool:
        """!Returns True if all values in the given list are not None"""
        return cache_values and all(cache_value is not None for cache_value in cache_values)


class CacheProvider:
    @staticmethod
    def get_cache(cache_type: Cache.Type) -> Cache:
        """!Creates and returns a new cache instance according to the requested cache type

        :param cache_type: enum representing the desired cache type
        :return: a new cache instance according to the requested cache type
        """
        if cache_type == Cache.Type.NONE:
            return DoNothingCache()
        elif cache_type == Cache.Type.REDIS:
            return RedisCache()
        elif cache_type == Cache.Type.IN_MEMORY:
            return InMemoryCache()
        else:
            raise AttributeError(f"Unsupported cache type {cache_type}")


class DoNothingCache(Cache):
    """!Empty implementation of the Cache interface. Does absolutely nothing."""

    def __init__(self) -> None:
        super().__init__()

    def status(self) -> bool:
        """!Empty implementation - returns True"""
        return True

    def get(self, keys: List[str]) -> List[Any]:
        """!Empty implementation - returns an empty list"""
        return []

    def set(self, cache_items: List[CacheItem]) -> None:
        """!Empty implementation - does nothing"""
        pass


class InMemoryCache(Cache):
    """!An in-memory implementation of the Cache interface.
    WARNING: This cache is not intended for production!!!
    It can be useful in testing and in cases where a quick out-of-the-box implementation is required.
    This cache has a size limit of 1 million items. When the limit is reached, the oldest item is deleted to make room
    for a new item.

    Attributes:
        max_size_bytes: a maximum cache size to prevent out-of-memory issue (500 MB by default).
    """

    def __init__(self, max_size_bytes: int = 500000000) -> None:  # 500 MB
        super().__init__()
        self.cache = collections.OrderedDict()
        self.max_size_bytes = max_size_bytes

    def status(self) -> bool:
        return True

    def get(self, keys: List[str]) -> List[Any]:
        retrieved_items = []
        for key in keys:
            if key in self.cache:
                retrieved_items.append(self.cache[key])
            else:
                retrieved_items.append(None)
        return retrieved_items

    def set(self, cache_items: List[CacheItem]) -> None:
        for cache_item in cache_items:
            while sys.getsizeof(self.cache) + sys.getsizeof(cache_item) > self.max_size_bytes:
                # Cache is full, remove the oldest item
                self.cache.popitem(last=False)
            self.cache[cache_item.key] = cache_item.value
