from __future__ import annotations

import time
from dataclasses import dataclass


class Clock:
    """Time source interface."""

    def now(self) -> float:
        raise NotImplementedError


class MonotonicClock(Clock):
    """Uses `time.monotonic()` for safe elapsed-time measurement."""

    def now(self) -> float:
        return time.monotonic()


@dataclass
class ManualClock(Clock):
    """A controllable clock for tests."""

    t: float = 0.0

    def now(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("seconds must be non-negative")
        self.t += seconds
