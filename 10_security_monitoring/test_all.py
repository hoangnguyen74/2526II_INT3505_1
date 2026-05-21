"""Test script cho buoi 10"""
import httpx, json

BASE = "http://localhost:8002"

# 1. Circuit Breaker
print("=== Circuit Breaker Test ===")
for i in range(8):
    r = httpx.get(f"{BASE}/api/external/payment-gateway")
    body = r.json()
    msg = body.get("message", "")
    if not msg and "detail" in body:
        d = body["detail"]
        msg = d.get("message", str(d)) if isinstance(d, dict) else str(d)
    print(f"  Call {i+1}: {r.status_code} - {msg[:60]}")

r = httpx.get(f"{BASE}/api/external/circuit-status")
data = r.json()
print(f"\nCircuit State: {data['state']}, Failures: {data['failure_count']}/{data['failure_threshold']}")

# Reset
httpx.post(f"{BASE}/api/external/circuit-reset")
print("Circuit reset -> CLOSED")

# 2. Rate Limit
print("\n=== Rate Limit Test ===")
for i in range(13):
    r = httpx.get(f"{BASE}/api/limited")
    remaining = r.headers.get("x-ratelimit-remaining", "N/A")
    print(f"  Req {i+1}: {r.status_code} (remaining: {remaining})")

# 3. XSS test
print("\n=== XSS Test ===")
r = httpx.post(f"{BASE}/api/products", json={"name": "<script>alert(1)</script>", "price": 1000})
print(f"  XSS payload: {r.status_code} - {r.json()}")

# 4. Metrics
print("\n=== Metrics ===")
r = httpx.get(f"{BASE}/metrics")
for line in r.text.split("\n"):
    if line and not line.startswith("#"):
        print(f"  {line}")
