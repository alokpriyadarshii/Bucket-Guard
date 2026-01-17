# Bucket-Guard
BucketGuard is a lightweight, thread safe Token Bucket rate limiter for Python. It supports bursts plus steady refill an injectable clock for deterministic tests, and a try consume API that's concurrency safe. A FastAPI middleware demo returns 429 when limits are exceeded. Set capacity and refill (tokens/sec); includes tests and examples for reuse.
