from collections import OrderedDict
from dependency_injector.wiring import Provide, inject
import marshal
import objsize
import sys
from tarvis.common import time
from threading import Lock


class LocalCacheEntry:
    def __init__(self, value, ttl: float | None, size: int):
        self.value = value
        self.size = size
        if ttl is None:
            self.expiration = None
        else:
            self.expiration = time.time() + ttl

    def is_expired(self) -> bool:
        if self.expiration is not None:
            return time.time() < self.expiration
        return False


class LocalCache:
    def __init__(
        self,
        default_ttl: float | None = None,
        max_size_bytes: int | None = None,
        max_items: int = sys.maxsize,
    ):
        self._cache = OrderedDict()
        self._lock = Lock()
        self._default_ttl = default_ttl
        self._max_size = max_size_bytes
        self._max_items = max_items
        self._size = 0
        self._item_count = 0

    def get(self, key: any, default: any = None):
        with self._lock:
            try:
                entry = self._cache.pop(key)
            except KeyError:
                return default
            if entry.is_expired():
                self._size -= entry.size
                self._item_count -= 1
                return default
            self._cache[key] = entry
            return entry.value

    def set(self, key: any, value: any, ttl: float | None = None):
        with self._lock:
            try:
                entry = self._cache.pop(key)
                self._size -= entry.size
                self._item_count -= 1
            except KeyError:
                pass
            if ttl is None:
                ttl = self._default_ttl
            entry_size = len(key) + objsize.get_deep_size(value)
            entry = LocalCacheEntry(value, ttl, entry_size)
            self._cache[key] = entry
            self._size += entry.size
            self._item_count += 1
            if self._item_count > self._max_items:
                key, entry = self._cache.popitem(last=False)
                self._size -= entry.size
                self._item_count -= 1
            if self._max_size is not None:
                while self._size > self._max_size:
                    key, entry = self._cache.popitem(last=False)
                    self._size -= entry.size
                    self._item_count -= 1

    def delete(self, key: any):
        with self._lock:
            try:
                entry = self._cache.pop(key)
                self._size -= entry.size
                self._item_count -= 1
            except KeyError:
                pass

    def purge(self):
        with self._lock:
            self._cache.clear()
            self._size = 0
            self._item_count = 0


_LOCAL_CACHE_MAX_SIZE_BYTES_DEFAULT = 512 * 1024

_lock = Lock()
_local_cache: LocalCache | None = None


@inject
def get_local_cache(config: dict = Provide["config"]) -> LocalCache:
    global _local_cache
    if _local_cache is not None:
        return _local_cache
    else:
        with _lock:
            if _local_cache is None:
                cache_config = config.get("local_cache")
                if cache_config is not None:
                    default_ttl = cache_config.get("default_ttl")
                    max_size_bytes = cache_config.get(
                        "max_size_bytes", _LOCAL_CACHE_MAX_SIZE_BYTES_DEFAULT
                    )
                    max_items = cache_config.get("max_items", sys.maxsize)
                    _local_cache = LocalCache(
                        default_ttl=default_ttl,
                        max_size_bytes=max_size_bytes,
                        max_items=max_items,
                    )
            return _local_cache


def create_cache_key(*args) -> bytes:
    return marshal.dumps(args)
