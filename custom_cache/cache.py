import asyncio
import threading
from collections import OrderedDict, defaultdict
from typing import Any

from custom_cache.cache_enum import *


class Cache:
    def __init__(self, capacity, db_service, ttl=None,
                 write_policy=WritePolicy.WRITE_THROUGH, refresh_interval=None, refresh_check=30):
        self.capacity = capacity
        self.ttl = ttl
        self.write_policy = write_policy
        self.refresh_interval = refresh_interval
        self.cache = {}
        self.lock = threading.Lock()
        self.db_service = db_service
        self.refresh_check = refresh_check

    def put(self, key: str, value: Any):
        raise NotImplementedError

    def get(self, key: str) -> Any:
        raise NotImplementedError

    def remove(self, key: str):
        raise NotImplementedError


    def _evict(self):
        raise NotImplementedError

    def _refresh(self):
        raise NotImplementedError

