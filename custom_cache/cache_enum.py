from enum import Enum


# Write  Policies
class WritePolicy(Enum):
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"


# Eviction Policies
class EvictionPolicy(Enum):
    LRU = "lru"
    LFU = "lfu"
