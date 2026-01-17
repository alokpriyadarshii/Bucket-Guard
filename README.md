# Bucket Guard

set -euo pipefail

# 1) Go to project folder (adjust if you're already there)
cd "BucketGuard"

# 2) Create + activate a fresh venv
rm -rf .venv
python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv
source .venv/bin/activate

# 3) Install deps (incl dev deps for tests + fastapi demo)
python -m pip install -U pip
python -m pip install -e ".[dev,fastapi]"
python -m pip install "uvicorn[standard]"

# 4) Run tests
pytest

# 5) Verify library import + basic behavior
echo "== bucket smoke test =="
python -c "from rate_limiter_token_bucket import TokenBucket; b=TokenBucket(capacity=10, refill_rate=5); print('consume(1)=', b.try_consume(1)); print('tokens=', b.tokens_available())"

# 6) Start FastAPI demo in background
API_HOST=127.0.0.1
PORT=8000
API="http://${API_HOST}:${PORT}"
uvicorn fastapi_demo:app --host "$API_HOST" --port "$PORT" --app-dir examples >/tmp/bucketguard.log 2>&1 & PID=$!
trap 'kill "$PID" 2>/dev/null || true' EXIT INT TERM

# 7) Wait until server is ready
until curl -sf "$API/" >/dev/null; do sleep 0.2; done

# 8) Demo API calls
echo "== root =="; curl -s "$API/" | python -m json.tool

echo "== burst test (20 quick requests; expect 200 then 429) =="
for i in {1..20}; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$API/")
  echo "$i -> $code"
done

echo "== refill (sleep 1s) then try again =="
sleep 1
curl -i "$API/" | sed -n '1,20p'

echo "Done. Server will stop now. Logs: /tmp/bucketguard.log"
