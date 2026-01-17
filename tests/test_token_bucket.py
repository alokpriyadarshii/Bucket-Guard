from __future__ import annotations

import math

import pytest

from rate_limiter_token_bucket import ManualClock, TokenBucket


def test_basic_consume_and_refill() -> None:
    clock = ManualClock(0.0)
    bucket = TokenBucket(capacity=5, refill_rate=1, clock=clock)

    assert bucket.tokens_available() == 5
    assert bucket.try_consume(3) is True
    assert bucket.tokens_available() == 2
    assert bucket.try_consume(3) is False

    clock.advance(2)
    assert math.isclose(bucket.tokens_available(), 4, rel_tol=1e-9)
    assert bucket.try_consume(4) is True
    assert bucket.tokens_available() == 0


def test_time_to_availability() -> None:
    clock = ManualClock(0.0)
    bucket = TokenBucket(capacity=2, refill_rate=2, clock=clock)
    assert bucket.try_consume(2) is True
    assert bucket.time_to_availability(1) == 0.5
    clock.advance(0.5)
    assert bucket.try_consume(1) is True


def test_invalid_params() -> None:
    with pytest.raises(ValueError):
        TokenBucket(capacity=0, refill_rate=1)
    with pytest.raises(ValueError):
        TokenBucket(capacity=1, refill_rate=0)
