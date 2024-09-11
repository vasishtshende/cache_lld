import time
import unittest
from unittest.mock import patch

from custom_cache.cache_factory import CacheFactory
from custom_cache.database import DatabaseFactory
from custom_cache.exceptions import KeyNotFoundException
from custom_cache.cache_enum import WritePolicy, EvictionPolicy
from custom_cache.storage_service import SqliteService


class TestCache(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # This runs once for all tests
        cls.sqlite_handler = DatabaseFactory.get_database_handler()
        cls.sqlite_handler.connect()
        cls.sqlite_service = SqliteService(cls.sqlite_handler)
        cls.sqlite_service.create_cache_storage_table()

    @classmethod
    def tearDownClass(cls):
        cls.sqlite_handler.close()

    def setUp(self):
        self.lru_cache = CacheFactory.create_cache(eviction_policy=EvictionPolicy.LRU, capacity=2,
                                                   db_service=self.sqlite_service, ttl=3,
                                                   write_policy=WritePolicy.WRITE_BACK, refresh_interval=None,
                                                   refresh_check=3)

    def test_ttl_eviction_policy(self):
        self.lru_cache.put('key1', 'value1')
        self.sqlite_service.insert_entry_in_storage('key1', 'value2')
        self.assertEqual(self.lru_cache.get('key1'), 'value1')
        time.sleep(5)
        # simulating async io thread sleep in single thread
        self.lru_cache._evict_expired_entries()
        self.assertEqual(self.lru_cache.get('key1'), 'value2')



if __name__ == '__main__':
    unittest.main()
