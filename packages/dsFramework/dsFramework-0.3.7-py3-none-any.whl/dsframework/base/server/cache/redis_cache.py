import redis
import logging
from typing import List, Any
from redis import RedisError
from dsframework.base.server.cache.cache import CacheItem, Cache

logger = logging.getLogger(__name__)


class RedisCache(Cache):
    """!The Redis implementation of the Cache interface. Uses a StrictRedis as the underlying Redis client.

    Attributes:
        host: the Redis server connection host (localhost by default)
        port: the Redis server connection port (6379 by default)
        ttl_seconds: time-to-live - how long before items are evicted from the cache (30 days by default)
    """

    def __init__(self, host: str = 'localhost', port: int = 6379,
                 ttl_seconds: int = 60 * 60 * 24 * 30, socket_timeout: int = 5) -> None:
        self.redis_client: redis.client.Redis = redis.StrictRedis(host=host, port=port, socket_timeout=socket_timeout)
        self.redis_connected: bool = False
        self.host: str = host
        self.port: int = port
        self.ttl_seconds: int = ttl_seconds  # time-to-live: items expire from cache after 30 days by default

    def init(self):
        """!Initialization for the cache in any manner (for example: connect)"""
        self.connect()

    # noinspection PyBroadException
    def connect(self):
        """!Connects the client to the Redis server"""
        logger.info("Connecting to Redis...")
        self.redis_client: redis.client.Redis = redis.StrictRedis(host=self.host, port=self.port, socket_timeout=5)
        self.redis_connected = False
        try:
            self.redis_client.ping()
            self.redis_connected = True
            logger.info('Connected to Redis successfully')
        except Exception:
            logger.exception('ERROR Failed connecting to Redis')
            return

    def status(self) -> bool:
        """!Indicates if the cache client is ready for work or not.

        :return: True when the cache client is ready for work, False otherwise
        """
        return self.redis_connected

    def get(self, keys: List[str]) -> List[Any]:
        """!Retrieves one or more items from the cache

        :param keys: the list of keys to retrieve items for
        :return: a list of one or more items corresponding to the given list of keys
        """
        retrieved_items = []
        if not self.redis_connected:
            return []
        try:
            retrieved_items = self.redis_client.mget(keys)  # retrieve multiple keys
        except RedisError as ex:
            exception_type = type(ex).__name__
            logger.error(f'ERROR Failed retrieving items from Redis cache - {keys} - {exception_type}')
            if exception_type == 'ConnectionError':
                self.redis_connected = False
        return retrieved_items

    def set(self, cache_items: List[CacheItem]):
        """!Stores one or more items in the cache

        :param cache_items: the list of CacheItems (key:value pairs) to be stored
        """
        if not self.redis_connected:
            return
        try:
            pipe = self.redis_client.pipeline(transaction=False)
            for cache_item in cache_items:
                pipe.set(name=cache_item.key, value=cache_item.value, ex=self.ttl_seconds)
            pipe.execute()
        except RedisError as ex:
            exception_type = type(ex).__name__
            logger.error(f'ERROR Failed storing items in Redis cache - {cache_items} - {exception_type}')
            if exception_type == 'ConnectionError':
                self.redis_connected = False
