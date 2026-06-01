import time
import threading
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl: int = 60, max_size: int = 512):
        self._ttl = ttl
        self._max_size = max_size
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            if len(self._store) >= self._max_size:
                self._evict()
            self._store[key] = (value, time.monotonic() + (ttl or self._ttl))

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def _evict(self) -> None:
        now = time.monotonic()
        expired = [k for k, (_, exp) in self._store.items() if exp <= now]
        for k in expired:
            del self._store[k]
        if len(self._store) >= self._max_size:
            del self._store[min(self._store, key=lambda k: self._store[k][1])]


price_cache = TTLCache(ttl=15, max_size=256)
market_cache = TTLCache(ttl=30, max_size=128)
signal_cache = TTLCache(ttl=300, max_size=64)
