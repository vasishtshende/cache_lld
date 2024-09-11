import asyncio
import logging
import time
from collections import defaultdict
from custom_cache.cache import Cache
from custom_cache.exceptions import *
from custom_cache.write_policies import WritePolicyFactory


class LFUCache(Cache):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frequency = defaultdict(int)
        self.write_policy_obj = WritePolicyFactory.get_write_policy(self.write_policy, self._write_to_store)

        if not self.refresh_check:
            raise ValueError("Please provide a valid value for refresh_check.")

        self._start_refresh_task()

        logging.info("LFU Cache created.")

    def put(self, key, value):
        try:
            with self.lock:
                self.frequency[key] += 1
                self.cache[key] = (value, time.time())
                if len(self.cache) > self.capacity:
                    self._evict()

                # Delegate writing operation to the write policy object
                self.write_policy_obj.write(key, value)

        except Exception as e:
            raise CacheException(f"An unexpected error occurred while writing to the cache: {key}-{value}. Error: {e}")

    def get(self, key):
        try:
            with self.lock:
                if key in self.cache:
                    self.frequency[key] += 1
                    return self.cache[key][0]
                raise CacheMissException(f"Key '{key}' not found in cache.")
        except CacheMissException as e:
            logging.info(e)
            result = self.db_service.get_entry_from_storage(key)
            if result:
                self.cache[key] = (result, time.time())
                if len(self.cache) > self.capacity:
                    self._evict()
            return result
        except Exception as e:
            raise CacheException(f"An unexpected error occurred while getting key from cache: {key}. Error: {e}")

    def remove(self, key):
        try:
            with self.lock:
                if key in self.cache:
                    del self.cache[key]
                    del self.frequency[key]
                else:
                    raise KeyNotFoundException(f"Key '{key}' not found in cache.")
        except Exception as e:
            raise CacheException(f"An unexpected error occurred while removing key from cache: {key}. Error: {e}")

    def _evict(self):
        try:
            least_frequent = min(self.frequency, key=self.frequency.get)
            evicted_item = self.cache.pop(least_frequent)
            del self.frequency[least_frequent]
            logging.info(f"Evicted item: {least_frequent} -> {evicted_item}")

            # If using WRITE_BACK, write dirty entries to the store before eviction
            self.write_policy_obj.evict(least_frequent, evicted_item)

        except Exception as e:
            raise CacheException(f"An unexpected error occurred while evicting key from cache. Error: {e}")

    async def _refresh(self):
        try:
            while True:
                await asyncio.sleep(self.refresh_check)
                self._refresh_cache()
        except Exception as e:
            raise CacheException(f"An unexpected error occurred while refreshing the cache. Error: {e}")

    async def _expire(self):
        try:
            while True:
                await asyncio.sleep(self.refresh_check)
                self._evict_expired_entries()
        except Exception as e:
            raise CacheException(f"An unexpected error occurred while evicting expired entries from cache. Error: {e}")

    def _refresh_cache(self):
        try:
            with self.lock:
                now = time.time()
                expired_keys = [key for key, (_, timestamp) in self.cache.items() if now - timestamp > self.refresh_interval]

                for key in expired_keys:
                    fresh_value = self.db_service.get_entry_from_storage(key)
                    if fresh_value:
                        logging.info(f"Refreshing key '{key}' with new value from store.")
                        self.cache[key] = (fresh_value, time.time())
                    else:
                        logging.info(f"Skipping refresh of key '{key}' in cache.")
        except Exception as e:
            raise CacheException(f"An unexpected error occurred while refreshing cache. Error: {e}")

    def _evict_expired_entries(self):
        try:
            with self.lock:
                now = time.time()
                expired_keys = [key for key, (_, timestamp) in self.cache.items() if now - timestamp > self.ttl]
                for key in expired_keys:
                    logging.info(f"Evicting expired key: {key}")
                    del self.cache[key]
        except Exception as e:
            raise CacheException(f"An unexpected error occurred while evicting expired entries from cache. Error: {e}")

    def _write_to_store(self, key, value):
        try:
            self.db_service.insert_entry_in_storage(key, value)
        except Exception as e:
            raise CacheException(f"An error occurred while writing key '{key}' to the store. Error: {e}")

    def _start_refresh_task(self):
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                logging.warning("No event loop found; creating a new one.")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if self.refresh_interval:
                loop.create_task(self._refresh())
            if self.ttl:
                loop.create_task(self._expire())
        except Exception as e:
            logging.error(f"Unexpected error in starting refresh task: {e}")
            raise
