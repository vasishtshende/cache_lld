from abc import ABC, abstractmethod

from custom_cache import WritePolicy
from custom_cache.exceptions import CacheException


class WritePolicyBase(ABC):

    def __init__(self, write_callback):
        self.write_callback = write_callback

    @abstractmethod
    def write(self, key, value):
        pass


class WriteThroughPolicy(WritePolicyBase):

    def write(self, key, value):
        self.write_callback(key, value)

    def evict(self, key, value):
        pass


class WriteBackPolicy(WritePolicyBase):

    def __init__(self, write_callback):
        super().__init__(write_callback)
        self.dirty = set()

    def write(self, key, value):
        self.dirty.add(key)

    def evict(self, key, value):
        if key in self.dirty:
            self.write_callback(key, value)
            self.dirty.remove(key)

    def flush(self, cache):
        for key in list(self.dirty):
            value, _ = cache.cache[key]
            self.write_callback(key, value)
            self.dirty.remove(key)


class WritePolicyFactory:

    @staticmethod
    def get_write_policy(write_policy_type, write_callback):
        if write_policy_type == WritePolicy.WRITE_THROUGH:
            return WriteThroughPolicy(write_callback)
        elif write_policy_type == WritePolicy.WRITE_BACK:
            return WriteBackPolicy(write_callback)
        else:
            raise CacheException("Invalid Write Policy")
