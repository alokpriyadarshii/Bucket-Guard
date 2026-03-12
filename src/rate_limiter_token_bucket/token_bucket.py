from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Optional

from .clock import Clock, MonotonicClock


@dataclass
class TokenBucketConfig:
    capacity: float
    refill_rate: float  # tokens per second

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("capacity must be > 0")
        if self.refill_rate <= 0:
            raise ValueError("refill_rate must be > 0")


class TokenBucket:
    """Token bucket rate limiter.

    - `capacity`: max burst size
    - `refill_rate`: tokens added per second

    This implementation is thread-safe.
    """

    def __init__(self, capacity: float, refill_rate: float, *, clock: Optional[Clock] = None) -> None:
        self.config = TokenBucketConfig(capacity=capacity, refill_rate=refill_rate)
        self._clock = clock or MonotonicClock()
        self._lock = Lock()
        self._tokens: float = capacity
        self._last_ts: float = self._clock.now()

    def try_consume(self, tokens: float = 1.0) -> bool:
        """Attempt to consume tokens. Returns True if allowed."""
        if tokens <= 0:
            raise ValueError("tokens must be > 0")
        if tokens > self.config.capacity:
            raise ValueError("tokens must be <= capacity")
        with self._lock:
            self._refill_locked()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def tokens_available(self) -> float:
        """Return current token count (after refill)."""
        with self._lock:
            self._refill_locked()
            return self._tokens

    def time_to_availability(self, tokens: float = 1.0) -> float:
        """Seconds until `tokens` would be available (0 if already available)."""
        if tokens <= 0:
            raise ValueError("tokens must be > 0")
        if tokens > self.config.capacity:
            raise ValueError("tokens must be <= capacity")
        with self._lock:
            self._refill_locked()
            missing = max(0.0, tokens - self._tokens)
            return missing / self.config.refill_rate if missing > 0 else 0.0

    def _refill_locked(self) -> None:
        now = self._clock.now()
        elapsed = max(0.0, now - self._last_ts)
        self._last_ts = now
        self._tokens = min(self.config.capacity, self._tokens + elapsed * self.config.refill_rate)
