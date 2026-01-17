from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request

from rate_limiter_token_bucket import TokenBucket

app = FastAPI(title="Rate Limiter Demo")

# Simple per-process bucket. For production, use per-user/IP buckets in a cache.
bucket = TokenBucket(capacity=10, refill_rate=5)  # 5 req/sec, burst 10


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if not bucket.try_consume(1):
        raise HTTPException(status_code=429, detail="Too Many Requests")
    return await call_next(request)


@app.get("/")
def root():
    return {"message": "ok"}
