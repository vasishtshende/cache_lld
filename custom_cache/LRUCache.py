import logging
import time

from custom_cache.cache import *
from custom_cache.exceptions import *
from custom_cache.write_policies import WritePolicyFactory


class LRUCache(Cache):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = OrderedDict()
        self.write_policy_obj = WritePolicyFactory.get_write_policy(self.write_policy, self._write_to_store)

        if not self.refresh_check:
            raise ValueError("Please provide valid value for refresh_check.")

        self._start_refresh_task()

        logging.info("LRU Cache created.")

    def put(self, key, value):
        try:

            with self.lock:
                if key in self.cache:
                    self.cache.move_to_end(key)
                self.cache[key] = (value, time.time())
                if len(self.cache) > self.capacity:
                    self._evict()

                self.write_policy_obj.write(key, value)

        except Exception:
            raise CacheException(f"An unexpected error occurred while writing to the cache: {key}-{value}")

    def get(self, key):
        try:

            with self.lock:
                now = time.time()
                if key in self.cache:
                    if now - self.cache[key][1] > self.ttl:
                        logging.info(f"Key '{key}' has expired and is being evicted.")
                        del self.cache[key]
                    else:
                        self.cache.move_to_end(key)
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
        except Exception:
            raise CacheException(f"An unexpected error occurred while getting key from cache: {key}")

    def remove(self, key):
        try:

            with self.lock:
                if key in self.cache:
                    value, _ = self.cache.get(key)
                    logging.info(f"Removing item: {key} -> {value}")

                    self.write_policy_obj.evict(key, value)
                    del self.cache[key]
                else:
                    raise KeyNotFoundException(f"Key '{key}' not found in cache.")

        except KeyNotFoundException as e:
            logging.warning(e)

    def _evict(self):
        try:
            key, (value, _) = self.cache.popitem(last=False)
            logging.info(f"Evicted item: {key} -> {value}")

            self.write_policy_obj.evict(key, value)

        except Exception:
            raise CacheException(f"An unexpected error occurred while evicting key from cache.")

    async def _refresh(self):
        try:

            while True:
                await asyncio.sleep(self.refresh_check)
                self._refresh_cache()
        except Exception:
            raise CacheException(f"An unexpected error occurred while evicting key from cache.")

    async def _expire(self):
        try:

            while True:
                await asyncio.sleep(self.refresh_check)
                self._evict_expired_entries()

        except Exception:
            raise CacheException(f"An unexpected error occurred while evicting key from cache.")

    def _refresh_cache(self):
        try:

            with self.lock:
                now = time.time()
                expired_keys = [key for key, (_, timestamp) in self.cache.items() if
                                now - timestamp > self.refresh_interval]

                for key in expired_keys:
                    fresh_value = self.db_service.get_entry_from_storage(key)
                    if fresh_value:
                        logging.info(f"Refreshing key '{key}' with new value from store.")
                        value, _ = self.cache[key]
                        self.cache[key] = (fresh_value, time.time())
                    else:
                        logging.info(f"Skipping refresh of key '{key}' in cache.")

        except Exception:
            raise CacheException(f"An unexpected error occurred while refreshing cache.")

    def _evict_expired_entries(self):
        try:

            with self.lock:
                now = time.time()
                expired_keys = [key for key, (_, timestamp) in self.cache.items() if now - timestamp > self.ttl]
                for key in expired_keys:
                    print(f"Evicting expired key: {key}")
                    del self.cache[key]

        except Exception:
            raise CacheException(f"An unexpected error occurred while evicting expired entries from cache.")

    def _write_to_store(self, key: str, value: Any):
        try:
            self.db_service.insert_entry_in_storage(key, value)
        except Exception as e:
            raise CacheException(f"An error occurred while writing key '{key}' to the store. Error: {e}")

    def show_all_cache(self, ):
        try:

            for k, v in self.cache.items():
                print(f"key:{k} value:{v}")
        except Exception:
            raise CacheException(f"An unexpected error occurred while visualising cache.")

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
