import asyncio
import time

from custom_cache.cache_enum import *
from custom_cache.cache_factory import CacheFactory
from custom_cache.database import DatabaseFactory
from custom_cache.storage_service import SqliteService


async def main():
    sqlite_handler = DatabaseFactory.get_database_handler()
    sqlite_handler.connect()
    sqlite_service = SqliteService(sqlite_handler)
    sqlite_service.create_cache_storage_table()

    cache = CacheFactory.create_cache(eviction_policy=EvictionPolicy.LRU, capacity=2, db_service=sqlite_service, ttl=12,
                                      write_policy=WritePolicy.WRITE_BACK, refresh_interval=1, refresh_check=1)
    # Basic Operations
    cache.put('key1', 'value1')
    cache.put('key2', 'value2')
    keys = sqlite_service.fetch_all_keys_from_storage()
    print("All keys in the storage:")
    for key in keys:
        print(key)
    cache.put('key3', 'value3')
    print("getting key1: ", cache.get('key1'))
    cache.put('key4', 'value4')
    cache.put('key4', 'value5')
    cache.show_all_cache()

    print("Sleeping..")
    await asyncio.sleep(10)

    cache.show_all_cache()

    # sqlite_service.insert_cache_entry('key1', 'value1')
    # sqlite_service.insert_cache_entry('key2', 'value2')

    keys = sqlite_service.fetch_all_keys_from_storage()
    print("All keys in the storage:")
    for key in keys:
        print(key)

    # print(sqlite_service.get_cache_entry('key1'))
    # print(sqlite_service.get_cache_entry('key3'))

    sqlite_handler.close()


if __name__ == "__main__":
    asyncio.run(main())
