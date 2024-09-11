import asyncio
import logging

from custom_cache.LFUCache import LFUCache
from custom_cache.LRUCache import LRUCache
from custom_cache.cache_enum import *
from custom_cache.exceptions import *


class CacheFactory:

    @staticmethod
    def create_cache(eviction_policy: EvictionPolicy, capacity, db_service, ttl=None,
                     write_policy=WritePolicy.WRITE_THROUGH, refresh_interval=None, refresh_check=None):
        try:

            if eviction_policy == EvictionPolicy.LRU:
                cache = LRUCache(capacity, db_service, ttl, write_policy, refresh_interval, refresh_check=refresh_check)

            elif eviction_policy == EvictionPolicy.LFU:
                cache = LFUCache(capacity, db_service, ttl, write_policy, refresh_interval, refresh_check=refresh_check)
            else:
                raise CacheException("Invalid Eviction Policy Type")

            return cache

        except CacheException as ce:
            logging.error(f"Cache creation failed due to eviction policy error: {ce}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during cache creation: {e}")
            raise CacheException("An unexpected error occurred during cache creation.")
