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
        self.lfu_cache = CacheFactory.create_cache(eviction_policy=EvictionPolicy.LFU, capacity=2,
                                                   db_service=self.sqlite_service,
                                                   ttl=12,
                                                   write_policy=WritePolicy.WRITE_THROUGH, refresh_interval=3,
                                                   refresh_check=3)

    def test_lfu_add_and_retrieve(self):
        self.lfu_cache.put('key1', 'value1')
        self.assertEqual(self.lfu_cache.get('key1'), 'value1')

    def test_lfu_update_existing_key(self):
        self.lfu_cache.put('key1', 'value1')
        self.lfu_cache.put('key1', 'value2')
        self.assertEqual(self.lfu_cache.get('key1'), 'value2')

    def test_lfu_evict_on_capacity(self):
        self.lfu_cache.put('key1', 'value1')
        self.lfu_cache.put('key2', 'value2')
        self.lfu_cache.get('key1')
        self.lfu_cache.put('key3', 'value3')
        self.lfu_cache.get('key3')

        with patch.object(self.lfu_cache.db_service, 'get_entry_from_storage', return_value='mock1') as mock_storage:
            value = self.lfu_cache.get('key2')

            mock_storage.assert_called_once_with('key2')

            self.assertEqual(value, 'mock1')

            self.assertEqual(self.lfu_cache.get('key2'), 'mock1')

    def test_lfu_remove_key(self):
        self.lfu_cache.put('key1', 'value1')
        self.lfu_cache.remove('key1')
        with patch.object(self.lfu_cache.db_service, 'get_entry_from_storage', return_value='mock1') as mock_storage:
            value = self.lfu_cache.get('key1')

            mock_storage.assert_called_once_with('key1')

            self.assertEqual(value, 'mock1')

            self.assertEqual(self.lfu_cache.get('key1'), 'mock1')


if __name__ == '__main__':
    unittest.main()
