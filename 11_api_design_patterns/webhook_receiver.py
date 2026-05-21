"""
Webhook Receiver — Server nhận và verify webhooks từ main.py

Chạy: py -m uvicorn webhook_receiver:app --port 8001
Xem events nhận được: http://localhost:8001/events
"""

from fastapi import FastAPI, Request, HTTPException
import hashlib, hmac, json
from datetime import datetime

app = FastAPI(title="Webhook Receiver Demo", description="Nhận webhook từ http://localhost:8000")

# Phải khớp với `secret` khi đăng ký webhook ở main server
WEBHOOK_SECRET = "demo-secret-123"

received: list[dict] = []


def verify_signature(body: bytes, signature_header: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


@app.post("/webhook")
async def receive_webhook(request: Request):
    """Endpoint nhận event. Verify chữ ký HMAC trước khi xử lý."""
    body      = await request.body()
    signature = request.headers.get("X-Webhook-Signature", "")
    event_type  = request.headers.get("X-Webhook-Event", "unknown")
    delivery_id = request.headers.get("X-Webhook-ID", "unknown")
    attempt     = request.headers.get("X-Delivery-Attempt", "1")

    if not verify_signature(body, signature, WEBHOOK_SECRET):
        raise HTTPException(401, "Invalid webhook signature")

    data = json.loads(body)
    entry = {
        "delivery_id":     delivery_id,
        "attempt":         int(attempt),
        "event_type":      event_type,
        "data":            data,
        "received_at":     datetime.utcnow().isoformat() + "Z",
        "signature_valid": True,
    }
    received.append(entry)
    print(f"\n[WEBHOOK] {event_type} | delivery={delivery_id} | attempt={attempt}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return {"status": "received", "event_type": event_type, "delivery_id": delivery_id}


@app.get("/events")
def list_events():
    """Xem tất cả events đã nhận."""
    return {"total": len(received), "events": received[-30:]}


@app.get("/")
def index():
    return {
        "message":        "Webhook receiver đang chạy tại port 8001",
        "endpoint":       "POST /webhook",
        "events_received": len(received),
        "note":           f"Đăng ký webhook với secret='{WEBHOOK_SECRET}' ở main server",
    }
