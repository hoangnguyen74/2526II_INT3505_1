"""
Buổi 11-12: API Design Patterns
Demo: Order Management System minh họa CRUD, Query, HATEOAS, Event-driven, Webhook

Chạy main server : py -m uvicorn main:app --reload --port 8000
Chạy receiver    : py -m uvicorn webhook_receiver:app --port 8001
Docs             : http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Request, Query as Q
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import asyncio, hashlib, hmac, json, random, time, uuid
from collections import defaultdict


# ══════════════════════════════════════════════
# 1. EVENT BUS  (Event-driven Pattern)
# ══════════════════════════════════════════════

class EventBus:
    """In-memory pub/sub. Subscribers đăng ký theo event_type hoặc "*" (wildcard)."""

    def __init__(self):
        self._subs: dict[str, list] = defaultdict(list)
        self._history: list[dict] = []

    def subscribe(self, event_type: str, handler):
        self._subs[event_type].append(handler)

    async def publish(self, event_type: str, data: dict) -> dict:
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        self._history.append(event)
        for handler in self._subs.get(event_type, []) + self._subs.get("*", []):
            await handler(event)
        return event

    @property
    def history(self) -> list[dict]:
        return self._history[-100:]


event_bus = EventBus()


# ══════════════════════════════════════════════
# 2. WEBHOOK ENGINE  (Stripe/GitHub-style)
# ══════════════════════════════════════════════

class WebhookEngine:
    """
    Quản lý đăng ký webhook và giao nhận event.
    Signature: X-Webhook-Signature: sha256=<hmac-sha256>
    Retry: tối đa 3 lần, exponential backoff (2s, 4s, 8s)
    """

    def __init__(self):
        self.webhooks: dict[str, dict] = {}
        self.deliveries: list[dict] = []

    def register(self, url: str, events: list[str], secret: str) -> dict:
        wh = {
            "id": f"wh_{uuid.uuid4().hex[:8]}",
            "url": url,
            "events": events,
            "secret": secret,
            "active": True,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        self.webhooks[wh["id"]] = wh
        return wh

    @staticmethod
    def sign(secret: str, payload: str) -> str:
        return "sha256=" + hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    async def deliver(self, webhook: dict, event: dict) -> dict:
        import httpx

        payload = json.dumps(event)
        delivery = {
            "id": f"wd_{uuid.uuid4().hex[:8]}",
            "webhook_id": webhook["id"],
            "event_id": event["id"],
            "event_type": event["type"],
            "url": webhook["url"],
            "status": "pending",
            "attempts": [],
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        for attempt in range(1, 4):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.post(
                        webhook["url"],
                        content=payload,
                        headers={
                            "Content-Type": "application/json",
                            "X-Webhook-Signature": self.sign(webhook["secret"], payload),
                            "X-Webhook-Event": event["type"],
                            "X-Webhook-ID": delivery["id"],
                            "X-Delivery-Attempt": str(attempt),
                        },
                    )
                delivery["attempts"].append({
                    "attempt": attempt,
                    "status_code": resp.status_code,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "success": resp.status_code < 300,
                })
                if resp.status_code < 300:
                    delivery["status"] = "delivered"
                    break
            except Exception as exc:
                delivery["attempts"].append({
                    "attempt": attempt,
                    "error": str(exc),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "success": False,
                })
                if attempt < 3:
                    await asyncio.sleep(2 ** attempt)   # 2s, 4s

        if delivery["status"] != "delivered":
            delivery["status"] = "failed"

        self.deliveries.append(delivery)
        return delivery

    async def dispatch(self, event: dict):
        """Gửi event đến tất cả webhook đang active và subscribe event type đó."""
        for wh in self.webhooks.values():
            if wh["active"] and (event["type"] in wh["events"] or "*" in wh["events"]):
                asyncio.create_task(self.deliver(wh, event))


webhook_engine = WebhookEngine()


async def _webhook_dispatcher(event: dict):
    await webhook_engine.dispatch(event)

event_bus.subscribe("*", _webhook_dispatcher)


# ══════════════════════════════════════════════
# 3. HATEOAS HELPERS
# ══════════════════════════════════════════════

def resource_links(collection: str, resource_id: str, **extra) -> dict:
    """Sinh _links cho một resource (HAL-style)."""
    return {
        "self": f"/api/v1/{collection}/{resource_id}",
        "collection": f"/api/v1/{collection}",
        **extra,
    }


def page_links(collection: str, page: int, total_pages: int, **params) -> dict:
    """Sinh _links cho paginated collection (first/prev/self/next/last)."""
    def url(p: int) -> str:
        qs = "&".join(f"{k}={v}" for k, v in {**params, "page": p}.items() if v is not None)
        return f"/api/v1/{collection}?{qs}"

    links = {"self": url(page), "first": url(1), "last": url(total_pages)}
    if page > 1:
        links["prev"] = url(page - 1)
    if page < total_pages:
        links["next"] = url(page + 1)
    return links


def order_state_links(order: dict) -> dict:
    """HATEOAS state machine: chỉ expose các transition hợp lệ từ trạng thái hiện tại."""
    oid = order["id"]
    links = resource_links("orders", oid,
        customer_orders=f"/api/v1/orders?customer_email={order['customer_email']}")

    transitions = {
        "pending":   ["confirmed", "cancelled"],
        "confirmed": ["shipped",   "cancelled"],
        "shipped":   ["delivered"],
    }
    for next_status in transitions.get(order["status"], []):
        links[next_status] = {
            "href": f"/api/v1/orders/{oid}/status",
            "method": "PATCH",
            "body": {"status": next_status},
        }
    return links


# ══════════════════════════════════════════════
# 4. IN-MEMORY STORES
# ══════════════════════════════════════════════

products_db: dict[str, dict] = {
    "prod_001": {"id": "prod_001", "name": "iPhone 16 Pro",  "price": 28_990_000, "category": "electronics", "stock": 50,  "created_at": "2025-01-01T00:00:00Z"},
    "prod_002": {"id": "prod_002", "name": "MacBook Air M3", "price": 27_490_000, "category": "electronics", "stock": 30,  "created_at": "2025-01-02T00:00:00Z"},
    "prod_003": {"id": "prod_003", "name": "AirPods Pro 2",  "price":  6_990_000, "category": "audio",       "stock": 100, "created_at": "2025-01-03T00:00:00Z"},
}

orders_db: dict[str, dict] = {}


# ══════════════════════════════════════════════
# 5. PYDANTIC MODELS
# ══════════════════════════════════════════════

class ProductCreate(BaseModel):
    name:     str = Field(..., min_length=1, max_length=200, examples=["Samsung Galaxy S25"])
    price:    int = Field(..., gt=0, examples=[22_990_000])
    category: str = Field("general", examples=["electronics"])
    stock:    int = Field(0, ge=0)


class OrderItem(BaseModel):
    product_id: str
    quantity:   int = Field(..., ge=1)


class OrderCreate(BaseModel):
    customer_email: str = Field(..., examples=["alice@example.com"])
    items:          list[OrderItem]
    notes:          Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., examples=["confirmed"],
                        description="pending → confirmed/cancelled | confirmed → shipped/cancelled | shipped → delivered")
    note: Optional[str] = None


class WebhookCreate(BaseModel):
    url:    str  = Field(..., examples=["http://localhost:8001/webhook"])
    events: list[str] = Field(["*"], examples=[["order.created", "order.confirmed"]])
    secret: str  = Field(default_factory=lambda: uuid.uuid4().hex,
                         examples=["demo-secret-123"])


# ══════════════════════════════════════════════
# 6. APP
# ══════════════════════════════════════════════

app = FastAPI(
    title="API Design Patterns Demo",
    description="Buổi 11-12: CRUD · Query · HATEOAS · Event-driven · Webhook",
    version="1.0.0",
    openapi_tags=[
        {"name": "1. CRUD Pattern",           "description": "Create / Read / Update / Delete chuẩn REST"},
        {"name": "2. Query Pattern",           "description": "Filtering · Sorting · Sparse Fieldsets · Pagination"},
        {"name": "3. HATEOAS + State Machine", "description": "Hypermedia links + state-driven navigation"},
        {"name": "4. Event-driven",            "description": "Domain events & event log"},
        {"name": "5. Webhook Pattern",         "description": "Đăng ký webhook, ký HMAC, retry, delivery log"},
        {"name": "Bonus",                      "description": "So sánh REST / gRPC / GraphQL, phân tích Stripe & GitHub"},
    ],
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ══════════════════════════════════════════════
# PATTERN 1: CRUD  (Products)
# ══════════════════════════════════════════════

@app.get("/api/v1/products", tags=["1. CRUD Pattern"])
async def list_products(
    page:      int            = Q(1,    ge=1),
    limit:     int            = Q(10,   ge=1, le=100),
    category:  Optional[str]  = None,
    min_price: Optional[int]  = None,
    max_price: Optional[int]  = None,
    q:         Optional[str]  = Q(None, description="Full-text search theo tên"),
    sort:      str            = Q("created_at:desc", description="field:asc hoặc field:desc"),
):
    """**CRUD List** kết hợp Query Pattern: filter, search, sort, paginate + HATEOAS links."""
    items = list(products_db.values())

    # Filter
    if category:   items = [p for p in items if p["category"] == category]
    if min_price is not None: items = [p for p in items if p["price"] >= min_price]
    if max_price is not None: items = [p for p in items if p["price"] <= max_price]
    if q:          items = [p for p in items if q.lower() in p["name"].lower()]

    # Sort
    field, _, direction = sort.partition(":")
    items.sort(key=lambda x: x.get(field, ""), reverse=(direction == "desc"))

    # Paginate
    total       = len(items)
    total_pages = max(1, (total + limit - 1) // limit)
    items       = items[(page - 1) * limit: page * limit]

    for p in items:
        p["_links"] = resource_links("products", p["id"])

    return {
        "data":  items,
        "meta":  {"total": total, "page": page, "limit": limit, "total_pages": total_pages},
        "_links": page_links("products", page, total_pages, limit=limit),
    }


@app.post("/api/v1/products", status_code=201, tags=["1. CRUD Pattern"])
async def create_product(body: ProductCreate):
    """**CRUD Create** + publish `product.created` event."""
    product = {"id": f"prod_{uuid.uuid4().hex[:6]}", "created_at": datetime.utcnow().isoformat() + "Z",
               **body.model_dump()}
    products_db[product["id"]] = product
    await event_bus.publish("product.created", {"product": product})
    product["_links"] = resource_links("products", product["id"])
    return product


@app.get("/api/v1/products/{product_id}", tags=["1. CRUD Pattern"])
def get_product(product_id: str):
    """**CRUD Read** + HATEOAS: link tới orders của sản phẩm này."""
    if product_id not in products_db:
        raise HTTPException(404, "Product not found")
    p = dict(products_db[product_id])
    p["_links"] = resource_links("products", product_id,
                                 orders=f"/api/v1/orders?product_id={product_id}")
    return p


@app.put("/api/v1/products/{product_id}", tags=["1. CRUD Pattern"])
async def update_product(product_id: str, body: ProductCreate):
    """**CRUD Update** + publish `product.updated`."""
    if product_id not in products_db:
        raise HTTPException(404, "Product not found")
    products_db[product_id].update(body.model_dump())
    p = dict(products_db[product_id])
    await event_bus.publish("product.updated", {"product": p})
    p["_links"] = resource_links("products", product_id)
    return p


@app.delete("/api/v1/products/{product_id}", status_code=204, tags=["1. CRUD Pattern"])
async def delete_product(product_id: str):
    """**CRUD Delete** + publish `product.deleted`."""
    if product_id not in products_db:
        raise HTTPException(404, "Product not found")
    deleted = products_db.pop(product_id)
    await event_bus.publish("product.deleted", {"product_id": product_id, "name": deleted["name"]})


# ══════════════════════════════════════════════
# PATTERN 2 & 3: QUERY + HATEOAS  (Orders)
# ══════════════════════════════════════════════

@app.post("/api/v1/orders", status_code=201, tags=["3. HATEOAS + State Machine"])
async def create_order(body: OrderCreate):
    """
    **HATEOAS**: Response chứa `_links` với các state transition khả dụng.

    **Event-driven**: Publish `order.created` → trigger webhook delivery.
    """
    items_detail, total = [], 0
    for item in body.items:
        if item.product_id not in products_db:
            raise HTTPException(404, f"Product {item.product_id} not found")
        p = products_db[item.product_id]
        subtotal = p["price"] * item.quantity
        total += subtotal
        items_detail.append({"product_id": item.product_id, "name": p["name"],
                              "price": p["price"], "quantity": item.quantity, "subtotal": subtotal})

    order = {
        "id": f"ord_{uuid.uuid4().hex[:8]}",
        "customer_email": body.customer_email,
        "items": items_detail,
        "total": total,
        "status": "pending",
        "notes": body.notes,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    orders_db[order["id"]] = order

    await event_bus.publish("order.created", {
        "order_id": order["id"],
        "customer_email": order["customer_email"],
        "total": order["total"],
        "status": "pending",
    })

    result = dict(order)
    result["_links"] = order_state_links(result)
    return result


@app.get("/api/v1/orders", tags=["2. Query Pattern"])
def list_orders(
    page:           int           = Q(1, ge=1),
    limit:          int           = Q(10, ge=1, le=100),
    status:         Optional[str] = None,
    customer_email: Optional[str] = None,
    min_total:      Optional[int] = None,
    max_total:      Optional[int] = None,
    sort:           str           = Q("created_at:desc"),
    fields:         Optional[str] = Q(None,
        description="**Sparse Fieldsets** — chỉ trả về các fields này, vd: `id,status,total`"),
):
    """
    **Query Pattern** đầy đủ:
    - Filtering theo status, email, khoảng giá
    - Sorting: `field:asc` / `field:desc`
    - **Sparse Fieldsets**: `?fields=id,status,total` (tiết kiệm bandwidth)
    - Pagination với HATEOAS links
    """
    items = list(orders_db.values())

    if status:         items = [o for o in items if o["status"] == status]
    if customer_email: items = [o for o in items if o["customer_email"] == customer_email]
    if min_total is not None: items = [o for o in items if o["total"] >= min_total]
    if max_total is not None: items = [o for o in items if o["total"] <= max_total]

    field, _, direction = sort.partition(":")
    items.sort(key=lambda x: x.get(field, ""), reverse=(direction == "desc"))

    total       = len(items)
    total_pages = max(1, (total + limit - 1) // limit)
    items       = items[(page - 1) * limit: page * limit]

    # Sparse Fieldsets
    allowed = set(fields.split(",")) if fields else None
    result_items = []
    for o in items:
        item = {k: v for k, v in o.items() if allowed is None or k in allowed}
        item["_links"] = resource_links("orders", o["id"])
        result_items.append(item)

    return {
        "data":  result_items,
        "meta":  {"total": total, "page": page, "limit": limit, "total_pages": total_pages},
        "_links": page_links("orders", page, total_pages, limit=limit),
    }


@app.get("/api/v1/orders/{order_id}", tags=["3. HATEOAS + State Machine"])
def get_order(order_id: str):
    """**HATEOAS**: Links thay đổi theo trạng thái — client không cần hardcode URL transitions."""
    if order_id not in orders_db:
        raise HTTPException(404, "Order not found")
    result = dict(orders_db[order_id])
    result["_links"] = order_state_links(result)
    return result


@app.patch("/api/v1/orders/{order_id}/status", tags=["3. HATEOAS + State Machine"])
async def update_order_status(order_id: str, body: OrderStatusUpdate):
    """
    **State Machine** với HATEOAS:

    ```
    pending ──► confirmed ──► shipped ──► delivered
       └──► cancelled    └──► cancelled
    ```

    Chỉ các transition hợp lệ được cho phép → 409 nếu vi phạm.
    """
    if order_id not in orders_db:
        raise HTTPException(404, "Order not found")

    order = orders_db[order_id]
    valid_transitions = {
        "pending":   ["confirmed", "cancelled"],
        "confirmed": ["shipped",   "cancelled"],
        "shipped":   ["delivered"],
        "delivered": [],
        "cancelled": [],
    }

    if body.status not in valid_transitions.get(order["status"], []):
        raise HTTPException(409, {
            "error":   "INVALID_TRANSITION",
            "message": f"Cannot move from '{order['status']}' to '{body.status}'",
            "allowed": valid_transitions.get(order["status"], []),
        })

    old_status     = order["status"]
    order["status"] = body.status
    order["updated_at"] = datetime.utcnow().isoformat() + "Z"

    await event_bus.publish(f"order.{body.status}", {
        "order_id":       order_id,
        "old_status":     old_status,
        "new_status":     body.status,
        "customer_email": order["customer_email"],
        "total":          order["total"],
    })

    result = dict(order)
    result["_links"] = order_state_links(result)
    return result


# ══════════════════════════════════════════════
# PATTERN 4: EVENT-DRIVEN  (Event log)
# ══════════════════════════════════════════════

@app.get("/api/v1/events", tags=["4. Event-driven"])
def get_events(event_type: Optional[str] = None):
    """
    **Event Log**: Xem toàn bộ domain events đã được publish trong session.

    Events kích hoạt: webhooks, audit log, notifications (có thể mở rộng thêm subscriber).
    """
    events = event_bus.history
    if event_type:
        events = [e for e in events if e["type"] == event_type]
    available_types = list({e["type"] for e in event_bus.history})
    return {
        "total":           len(events),
        "available_types": available_types,
        "events":          events[-20:],
        "_links":          {"self": "/api/v1/events"},
    }


# ══════════════════════════════════════════════
# PATTERN 5: WEBHOOK  (Stripe/GitHub-style)
# ══════════════════════════════════════════════

@app.post("/api/v1/webhooks", status_code=201, tags=["5. Webhook Pattern"])
def register_webhook(body: WebhookCreate):
    """
    **Đăng ký webhook** (Stripe-style):
    - Cung cấp URL nhận event và danh sách events cần subscribe
    - Hệ thống tạo `secret` để ký HMAC-SHA256 → client dùng để verify
    - `events: ["*"]` để nhận tất cả events
    """
    wh = webhook_engine.register(url=str(body.url), events=body.events, secret=body.secret)
    wh["_links"] = {
        "self":       f"/api/v1/webhooks/{wh['id']}",
        "deliveries": f"/api/v1/webhooks/{wh['id']}/deliveries",
        "test":       f"/api/v1/webhooks/{wh['id']}/test",
    }
    return wh


@app.get("/api/v1/webhooks", tags=["5. Webhook Pattern"])
def list_webhooks():
    """Liệt kê tất cả webhook đã đăng ký."""
    webhooks = []
    for wh in webhook_engine.webhooks.values():
        item = dict(wh)
        item["_links"] = {
            "self":       f"/api/v1/webhooks/{wh['id']}",
            "deliveries": f"/api/v1/webhooks/{wh['id']}/deliveries",
        }
        webhooks.append(item)
    return {"data": webhooks, "total": len(webhooks)}


@app.delete("/api/v1/webhooks/{webhook_id}", status_code=204, tags=["5. Webhook Pattern"])
def delete_webhook(webhook_id: str):
    """Hủy đăng ký webhook."""
    if webhook_id not in webhook_engine.webhooks:
        raise HTTPException(404, "Webhook not found")
    del webhook_engine.webhooks[webhook_id]


@app.post("/api/v1/webhooks/{webhook_id}/test", tags=["5. Webhook Pattern"])
async def test_webhook(webhook_id: str):
    """
    **Gửi test event** (giống nút "Send test webhook" của Stripe).

    Hữu ích để verify URL endpoint và chữ ký trước khi đưa vào production.
    """
    if webhook_id not in webhook_engine.webhooks:
        raise HTTPException(404, "Webhook not found")

    wh = webhook_engine.webhooks[webhook_id]
    test_event = await event_bus.publish("webhook.test", {
        "webhook_id": webhook_id,
        "message":    "This is a test event — ignore in production",
    })
    delivery = await webhook_engine.deliver(wh, test_event)
    return {"event": test_event, "delivery": delivery}


@app.get("/api/v1/webhooks/{webhook_id}/deliveries", tags=["5. Webhook Pattern"])
def webhook_deliveries(webhook_id: str):
    """
    **Delivery log** (giống GitHub webhook delivery history):
    - Xem từng lần giao event, số lần retry, kết quả
    """
    if webhook_id not in webhook_engine.webhooks:
        raise HTTPException(404, "Webhook not found")
    deliveries = [d for d in webhook_engine.deliveries if d["webhook_id"] == webhook_id]
    return {
        "data":  deliveries,
        "total": len(deliveries),
        "_links": {"self": f"/api/v1/webhooks/{webhook_id}/deliveries"},
    }


# ══════════════════════════════════════════════
# BONUS: Pattern Analysis — Stripe & GitHub
# ══════════════════════════════════════════════

@app.get("/api/v1/patterns/analysis", tags=["Bonus"])
def patterns_analysis():
    """
    **Phân tích patterns** quan sát từ Stripe và GitHub APIs.

    So sánh REST · gRPC · GraphQL và khi nào dùng cái nào.
    """
    return {
        "stripe_patterns": {
            "crud":        "POST /v1/customers | GET /v1/customers/{id} | DELETE /v1/customers/{id}",
            "query":       "GET /v1/charges?customer=cus_xxx&created[gte]=1700000000&limit=10",
            "pagination":  "Cursor-based: ?starting_after=ch_xxx (tránh offset drift khi dữ liệu thay đổi)",
            "idempotency": "Header Idempotency-Key: <uuid> — server lưu kết quả 24h, replay-safe",
            "versioning":  "Header Stripe-Version: 2024-06-20 — pin version per request",
            "webhook": {
                "signature":  "Stripe-Signature: t=<timestamp>,v1=<hmac-sha256>  (timestamp ngăn replay attack)",
                "events":     ["payment_intent.succeeded", "invoice.payment_failed", "customer.subscription.deleted"],
                "retry":      "Retry trong 3 ngày, exponential backoff, nếu server trả về status != 2xx",
                "idempotency": "Mỗi delivery có Stripe-Webhook-Id riêng — dùng để deduplicate",
            },
            "error_format": {"error": {"type": "card_error", "code": "card_declined", "message": "...", "param": "number"}},
        },
        "github_patterns": {
            "crud":       "GET /repos/{owner}/{repo} | PATCH /repos/{owner}/{repo} | DELETE ...",
            "hateoas":    "Mọi resource có *_url fields: comments_url, commits_url, labels_url...",
            "pagination": "Link header: <url>; rel='next', <url>; rel='last' — dùng header thay query",
            "webhook": {
                "signature":   "X-Hub-Signature-256: sha256=<hmac>",
                "delivery_id": "X-GitHub-Delivery: <uuid> — dùng để idempotent processing",
                "events":      ["push", "pull_request", "issues", "release", "workflow_run"],
            },
            "rest_vs_graphql": "REST /repos/{owner}/{repo} cho CRUD đơn giản; GraphQL /graphql cho query phức tạp (lấy PR + reviews + comments trong 1 request)",
            "rate_limiting": "X-RateLimit-Limit + X-RateLimit-Remaining + X-RateLimit-Reset (Unix timestamp)",
        },
        "when_to_use": {
            "REST": [
                "Public API — dễ document, debug bằng curl/Postman/browser",
                "CRUD resource đơn giản",
                "Cần HTTP cache (GET responses)",
                "Team không quen với Protobuf/schema",
            ],
            "gRPC": [
                "Internal microservice communication (latency thấp, throughput cao)",
                "Bidirectional streaming (chat, live feed)",
                "Strongly-typed contracts quan trọng (tự sinh client code từ .proto)",
                "Multi-language polyglot services",
            ],
            "GraphQL": [
                "Client cần linh hoạt chọn fields — tránh over/under-fetching",
                "Nhiều loại client khác nhau (mobile cần ít data hơn web)",
                "Aggregation từ nhiều data sources trong 1 request",
                "Real-time với Subscription (WebSocket)",
            ],
        },
    }
