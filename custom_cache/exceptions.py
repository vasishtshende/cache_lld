class CacheException(Exception):
    pass


class StorageException(Exception):
    pass


class KeyNotFoundException(CacheException):
    pass


class CacheFullException(CacheException):
    pass


class InvalidValueException(CacheException):
    pass


class CacheMissException(CacheException):
    pass


