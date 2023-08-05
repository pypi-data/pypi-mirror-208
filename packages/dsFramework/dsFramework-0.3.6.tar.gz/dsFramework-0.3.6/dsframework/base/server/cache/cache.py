from dataclasses import dataclass
from enum import Enum
from typing import Any, List


@dataclass
class CacheItem:
    """!Data class for passing (key,value) pairs into the cache"""
    key: str
    value: Any


class Cache:
    """!Generic cache interface. Does not contain any implementation."""

    class Type(Enum):
        """!Cache types Enum - NONE(0), REDIS(1), IN_MEMORY(2)"""
        NONE = 0
        REDIS = 1
        IN_MEMORY = 2  # for testing purposes only

    def init(self):
        """!Initialization for the cache in any manner (for example: connect)"""
        pass

    def get(self, keys: List[str]) -> List[Any]:
        """!Retrieve one or more items from the cache.

        :param keys: the list of keys to retrieve items for
        :return: a list of one or more items corresponding to the given list of keys
        """
        raise NotImplementedError

    def set(self, cache_items: List[CacheItem]) -> None:
        """!Store one or more items in the cache.

        :param cache_items: the list of CacheItems (key:value pairs) to be stored
        """
        raise NotImplementedError

    def status(self) -> bool:
        """!Indicate if the cache client is ready for work or not.

        :return: True if ready for work, False otherwise
        """
        raise NotImplementedError
