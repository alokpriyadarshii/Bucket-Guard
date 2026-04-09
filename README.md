# Bucket-Guard

A lightweight, thread safe Python token bucket rate limiter.

Bucket-Guard provides a simple implementation of the token bucket algorithm for controlling request throughput while still allowing short bursts of traffic. The project is packaged as a reusable library, includes unit tests, and ships with a small FastAPI example that shows how to apply the limiter to HTTP requests.

## Features

- Thread-safe token bucket implementation
- Configurable bucket capacity and refill rate
- Supports burst traffic up to bucket capacity
- Query current token availability
- Compute wait time until tokens are available
- Injectable clock abstraction for deterministic tests
- Optional FastAPI demo for API throttling

## How it works

The bucket starts full.

- `capacity` controls the maximum number of tokens stored
- `refill_rate` controls how many tokens are added per second
- each request consumes one or more tokens
- requests are allowed only when enough tokens are available

This makes the limiter suitable for cases where you want to permit short spikes in traffic while keeping long-term throughput bounded.

## Installation

### Requirements

- Python 3.11+

### Install the package locally

```bash
pip install -e .
```

### Install development dependencies

```bash
pip install -e ".[dev]"
```

### Install with FastAPI demo dependencies

```bash
pip install -e ".[fastapi]"
pip install "uvicorn[standard]"
```

## Quick start

```python
from rate_limiter_token_bucket import TokenBucket

bucket = TokenBucket(capacity=10, refill_rate=5)

if bucket.try_consume(1):
    print("request allowed")
else:
    print("rate limited")
```

## API overview

### `TokenBucket(capacity, refill_rate, clock=None)`

Creates a token bucket.

Parameters:

- `capacity`: maximum number of tokens the bucket can hold
- `refill_rate`: tokens added per second
- `clock`: optional custom clock implementation

### `try_consume(tokens=1.0) -> bool`

Attempts to consume tokens.

- returns `True` if enough tokens are available
- returns `False` if the request should be rejected
- raises `ValueError` if `tokens <= 0` or `tokens > capacity`

Example:

```python
bucket = TokenBucket(capacity=5, refill_rate=1)

print(bucket.try_consume(3))
print(bucket.try_consume(3))
```

### `tokens_available() -> float`

Returns the current token count after applying refill logic.

```python
remaining = bucket.tokens_available()
print(remaining)
```

### `time_to_availability(tokens=1.0) -> float`

Returns the number of seconds until the requested token amount becomes available.

```python
bucket = TokenBucket(capacity=2, refill_rate=2)
bucket.try_consume(2)
print(bucket.time_to_availability(1))
```

## Test-friendly clocks

The package exposes two clock implementations:

- `MonotonicClock`: production-safe clock based on `time.monotonic()`
- `ManualClock`: controllable clock for tests

Example:

```python
from rate_limiter_token_bucket import ManualClock, TokenBucket

clock = ManualClock(0.0)
bucket = TokenBucket(capacity=5, refill_rate=1, clock=clock)

bucket.try_consume(5)
print(bucket.tokens_available())

clock.advance(2)
print(bucket.tokens_available())
```

## FastAPI demo

The repository includes a simple demo in `examples/fastapi_demo.py`.

It uses one in-process shared bucket:

- capacity: `10`
- refill rate: `5` tokens per second

Start the demo:

```bash
uvicorn fastapi_demo:app --host 127.0.0.1 --port 8000 --app-dir examples
```

Then test it:

```bash
curl http://127.0.0.1:8000/
```

When the bucket is exhausted, the demo returns HTTP `429 Too Many Requests`.

## Running tests

```bash
pytest
```

Current test coverage includes:

- basic consume and refill behavior
- wait-time calculation
- invalid configuration handling
- rejection of requests larger than capacity

## Project structure

```text
Bucket-Guard/
├── examples/
│   └── fastapi_demo.py
├── src/
│   └── rate_limiter_token_bucket/
│       ├── __init__.py
│       ├── clock.py
│       └── token_bucket.py
├── tests/
│   └── test_token_bucket.py
├── pyproject.toml
└── README.md
```

## Development notes

- package name: `rate-limiter-token-bucket`
- import path: `rate_limiter_token_bucket`
- build backend: `setuptools`
- test framework: `pytest`

## Limitations

This repository currently focuses on a local in-memory token bucket.

That means:

- state is process-local
- the FastAPI demo is not distributed or multi-instance aware
- per-user, per-IP, or shared-cache strategies are not built in yet

For production API gateways or horizontally scaled services, you would typically maintain separate buckets keyed by client identity and back them with shared storage such as Redis.
