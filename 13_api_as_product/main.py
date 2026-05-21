"""
Buổi 13: API as a Product
Demo: Developer Portal — API key management, freemium quota, analytics, sandbox

Chạy : py -m uvicorn main:app --reload
Docs  : http://localhost:8000/docs
Portal: mở portal.html trong trình duyệt (double-click)
Admin : X-Admin-Key: admin-secret-key  →  GET /admin/analytics
"""

from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from collections import defaultdict
import secrets, time

# ══════════════════════════════════════════════
# 1. PRICING PLANS  (Freemium model)
# ══════════════════════════════════════════════

PLANS: dict[str, dict] = {
    "free": {
        "name": "Free",
        "price_usd": 0,
        "daily_quota": 100,
        "rate_limit_rpm": 10,
        "sla": None,
        "support": "Community",
        "features": ["100 calls/ngày", "Sandbox access", "Community support"],
    },
    "pro": {
        "name": "Pro",
        "price_usd": 29,
        "daily_quota": 10_000,
        "rate_limit_rpm": 200,
        "sla": "99.9%",
        "support": "Email (24h)",
        "features": ["10,000 calls/ngày", "SLA 99.9%", "Email support", "Search API", "Analytics"],
    },
    "enterprise": {
        "name": "Enterprise",
        "price_usd": 299,
        "daily_quota": None,          # Unlimited
        "rate_limit_rpm": 2000,
        "sla": "99.99%",
        "support": "24/7 Priority",
        "features": ["Unlimited calls", "SLA 99.99%", "24/7 Priority support",
                     "Custom rate limits", "Dedicated account manager", "SLA credits"],
    },
}

# ══════════════════════════════════════════════
# 2. IN-MEMORY STORES
# ══════════════════════════════════════════════

developers_db: dict[str, dict] = {}   # email → developer record
api_keys_db:   dict[str, dict] = {}   # api_key → developer record (same object)


def _make_dev(email: str, name: str, plan: str) -> dict:
    key = f"sk_{secrets.token_hex(16)}"
    dev = {
        "email":       email,
        "name":        name,
        "plan":        plan,
        "api_key":     key,
        "created_at":  datetime.utcnow().isoformat() + "Z",
        "daily_usage": defaultdict(int),   # date → call count
        "total_calls": 0,
        "error_calls": 0,
    }
    developers_db[email] = dev
    api_keys_db[key]     = dev
    return dev


# Seed demo data
_make_dev("alice@example.com", "Alice",  "pro")
_make_dev("bob@example.com",   "Bob",    "free")
_make_dev("carol@example.com", "Carol",  "enterprise")


# ══════════════════════════════════════════════
# 3. ANALYTICS TRACKER  (KPIs)
# ══════════════════════════════════════════════

class Analytics:
    def __init__(self):
        self.total_calls:       int            = 0
        self.error_calls:       int            = 0
        self.calls_by_endpoint: dict[str, int] = defaultdict(int)
        self.calls_by_plan:     dict[str, int] = defaultdict(int)
        self.start_time:        float          = time.time()

    def record(self, endpoint: str, plan: str, is_error: bool):
        self.total_calls += 1
        if is_error:
            self.error_calls += 1
        self.calls_by_endpoint[endpoint] += 1
        self.calls_by_plan[plan] += 1

    def kpis(self) -> dict:
        today = date.today().isoformat()
        active = sum(1 for d in developers_db.values() if d["daily_usage"][today] > 0)
        top_eps = sorted(self.calls_by_endpoint.items(), key=lambda x: x[1], reverse=True)[:5]
        mrr = sum(PLANS[d["plan"]]["price_usd"] for d in developers_db.values())
        return {
            "registered_developers": len(developers_db),
            "active_developers_today": active,
            "total_api_calls": self.total_calls,
            "error_rate_percent": round(self.error_calls / max(self.total_calls, 1) * 100, 2),
            "calls_by_plan": dict(self.calls_by_plan),
            "top_endpoints": [{"endpoint": e, "calls": c} for e, c in top_eps],
            "monthly_recurring_revenue_usd": mrr,
            "uptime_seconds": int(time.time() - self.start_time),
        }


analytics = Analytics()


# ══════════════════════════════════════════════
# 4. AUTH DEPENDENCY
# ══════════════════════════════════════════════

async def require_api_key(
    x_api_key: str = Header(..., description="API key dạng `sk_xxxxxxxx`"),
) -> dict:
    if x_api_key not in api_keys_db:
        raise HTTPException(401, {
            "error":   "INVALID_API_KEY",
            "message": "API key không hợp lệ.",
            "hint":    "Đăng ký miễn phí tại POST /developers/register",
        })

    dev   = api_keys_db[x_api_key]
    plan  = PLANS[dev["plan"]]
    today = date.today().isoformat()
    quota = plan["daily_quota"]
    used  = dev["daily_usage"][today]

    if quota is not None and used >= quota:
        raise HTTPException(429, {
            "error":       "QUOTA_EXCEEDED",
            "message":     f"Đã dùng hết {quota} calls/ngày của plan {dev['plan'].upper()}.",
            "used":        used,
            "limit":       quota,
            "reset_at":    f"{today}T23:59:59Z",
            "upgrade_url": "POST /developers/upgrade",
        })
    return dev


ADMIN_KEY = "admin-secret-key"


def require_admin(x_admin_key: str = Header(...)) -> None:
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(403, "Admin access only. Header: X-Admin-Key")


# ══════════════════════════════════════════════
# 5. APP
# ══════════════════════════════════════════════

app = FastAPI(
    title="API as a Product — Developer Portal",
    description=(
        "**Buổi 13**: API key management · Freemium quota · Analytics · Sandbox\n\n"
        "Admin key: `admin-secret-key` (Header: `X-Admin-Key`)"
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "Developer Portal", "description": "Đăng ký, lấy API key, xem quota & usage"},
        {"name": "Sandbox",          "description": "Test API không cần key, không tốn quota"},
        {"name": "API v1",           "description": "Endpoints thực — cần `X-API-Key`"},
        {"name": "Admin",            "description": "KPI dashboard & developer stats — cần `X-Admin-Key`"},
    ],
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def track_usage_middleware(request: Request, call_next):
    start    = time.time()
    response = await call_next(request)
    ms       = (time.time() - start) * 1000

    api_key = request.headers.get("x-api-key")
    if api_key and api_key in api_keys_db and request.url.path.startswith("/api/"):
        dev = api_keys_db[api_key]
        today = date.today().isoformat()
        dev["daily_usage"][today] += 1
        dev["total_calls"] += 1
        is_err = response.status_code >= 400
        if is_err:
            dev["error_calls"] += 1
        analytics.record(request.url.path, dev["plan"], is_err)

    response.headers["X-Response-Time"] = f"{ms:.1f}ms"
    return response


# ══════════════════════════════════════════════
# DEVELOPER PORTAL
# ══════════════════════════════════════════════

class RegisterRequest(BaseModel):
    email: str = Field(..., examples=["dev@example.com"])
    name:  str = Field(..., examples=["Nguyen Van A"])
    plan:  str = Field("free", examples=["free"])


class UpgradeRequest(BaseModel):
    email:    str = Field(..., examples=["dev@example.com"])
    new_plan: str = Field(..., examples=["pro"])


@app.get("/", tags=["Developer Portal"])
def api_home():
    """Trang chủ API — hướng dẫn bắt đầu nhanh."""
    return {
        "name":    "Product API v1.0",
        "tagline": "Fast, reliable product data API",
        "quick_start": [
            "1. POST /developers/register  → nhận api_key",
            "2. GET /api/v1/products  với header X-API-Key: sk_...",
            "3. GET /sandbox/products  để test không cần key",
        ],
        "links": {"docs": "/docs", "plans": "/plans", "sandbox": "/sandbox/products"},
    }


@app.get("/plans", tags=["Developer Portal"])
def list_plans():
    """Xem bảng giá — Freemium, Pro, Enterprise."""
    return {
        "plans": PLANS,
        "note": "Free plan không cần credit card. Nâng cấp bất cứ lúc nào.",
    }


@app.post("/developers/register", status_code=201, tags=["Developer Portal"])
def register(body: RegisterRequest):
    """
    **Đăng ký developer account** — nhận API key ngay lập tức.

    - Free plan: không cần credit card
    - Key được cấp tức thì, không cần phê duyệt *(tối ưu DX)*
    """
    if body.email in developers_db:
        raise HTTPException(409, {
            "error":   "EMAIL_EXISTS",
            "message": "Email đã đăng ký.",
            "hint":    f"Xem key tại GET /developers/{body.email}/usage",
        })
    if body.plan not in PLANS:
        raise HTTPException(400, {"error": "INVALID_PLAN", "valid": list(PLANS.keys())})

    dev  = _make_dev(body.email, body.name, body.plan)
    info = PLANS[body.plan]
    return {
        "message":    f"Chào mừng {body.name}! API key đã sẵn sàng.",
        "api_key":    dev["api_key"],
        "plan":       body.plan,
        "daily_quota": info["daily_quota"] or "Unlimited",
        "quick_start": f'curl -H "X-API-Key: {dev["api_key"]}" http://localhost:8000/api/v1/products',
    }


@app.get("/developers/{email}/usage", tags=["Developer Portal"])
def get_usage(email: str):
    """Xem usage, quota còn lại và lịch sử theo ngày."""
    if email not in developers_db:
        raise HTTPException(404, "Developer not found")

    dev   = developers_db[email]
    plan  = PLANS[dev["plan"]]
    today = date.today().isoformat()
    used  = dev["daily_usage"][today]
    quota = plan["daily_quota"]

    return {
        "email":   email,
        "name":    dev["name"],
        "plan":    dev["plan"],
        "api_key": dev["api_key"],
        "today": {
            "used":          used,
            "quota":         quota or "Unlimited",
            "remaining":     (quota - used) if quota else "Unlimited",
            "percent_used":  round(used / quota * 100, 1) if quota else 0,
        },
        "all_time": {
            "total_calls": dev["total_calls"],
            "error_calls": dev["error_calls"],
            "error_rate":  round(dev["error_calls"] / max(dev["total_calls"], 1) * 100, 2),
        },
        "daily_history": dict(dev["daily_usage"]),
    }


@app.post("/developers/upgrade", tags=["Developer Portal"])
def upgrade_plan(body: UpgradeRequest):
    """
    **Nâng cấp plan** — mô hình subscription.

    `free → pro ($29/mo) → enterprise ($299/mo)`
    """
    if body.email not in developers_db:
        raise HTTPException(404, "Developer not found")
    if body.new_plan not in PLANS:
        raise HTTPException(400, {"valid_plans": list(PLANS.keys())})

    dev      = developers_db[body.email]
    old_plan = dev["plan"]
    dev["plan"] = body.new_plan
    info = PLANS[body.new_plan]

    return {
        "message":     f"Nâng cấp thành công: {old_plan.upper()} → {body.new_plan.upper()}",
        "new_plan":    body.new_plan,
        "daily_quota": info["daily_quota"] or "Unlimited",
        "price":       f"${info['price_usd']}/tháng",
        "sla":         info["sla"] or "Không có SLA",
        "new_features": info["features"],
    }


# ══════════════════════════════════════════════
# SANDBOX  (không cần key, không tốn quota)
# ══════════════════════════════════════════════

@app.get("/sandbox/products", tags=["Sandbox"])
def sandbox_products():
    """
    **Sandbox**: Xem data mẫu không cần API key.

    Developer Experience: cho phép thử trước khi đăng ký.
    """
    return {
        "sandbox": True,
        "warning": "Data này là mẫu — không phản ánh data thực",
        "data": [
            {"id": "demo_001", "name": "[DEMO] iPhone 16 Pro",  "price": 28990000},
            {"id": "demo_002", "name": "[DEMO] MacBook Air M3", "price": 27490000},
        ],
        "get_real_data": "POST /developers/register để nhận API key miễn phí",
    }


@app.post("/sandbox/echo", tags=["Sandbox"])
async def sandbox_echo(request: Request):
    """**Sandbox echo**: gửi bất kỳ payload nào, nhận lại nguyên vẹn."""
    try:
        body = await request.json()
    except Exception:
        body = None
    return {
        "sandbox":   True,
        "echo":      body,
        "headers":   dict(request.headers),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ══════════════════════════════════════════════
# API v1  (cần API key + quota)
# ══════════════════════════════════════════════

_PRODUCTS = [
    {"id": "p001", "name": "iPhone 16 Pro",  "price": 28_990_000, "category": "electronics"},
    {"id": "p002", "name": "MacBook Air M3", "price": 27_490_000, "category": "electronics"},
    {"id": "p003", "name": "AirPods Pro 2",  "price":  6_990_000, "category": "audio"},
    {"id": "p004", "name": "iPad Pro M4",    "price": 23_990_000, "category": "electronics"},
    {"id": "p005", "name": "Apple Watch S10","price":  9_990_000, "category": "wearable"},
]


def _quota_header(dev: dict) -> dict:
    today = date.today().isoformat()
    quota = PLANS[dev["plan"]]["daily_quota"]
    used  = dev["daily_usage"][today]
    return {
        "X-Plan":             dev["plan"],
        "X-Quota-Limit":      str(quota) if quota else "Unlimited",
        "X-Quota-Remaining":  str(max(0, quota - used)) if quota else "Unlimited",
    }


from fastapi.responses import JSONResponse


@app.get("/api/v1/products", tags=["API v1"])
def get_products(dev: dict = Depends(require_api_key)):
    """Lấy danh sách sản phẩm — **yêu cầu API key**."""
    resp = JSONResponse({"data": _PRODUCTS, "count": len(_PRODUCTS)})
    for k, v in _quota_header(dev).items():
        resp.headers[k] = v
    return resp


@app.get("/api/v1/products/{product_id}", tags=["API v1"])
def get_product(product_id: str, dev: dict = Depends(require_api_key)):
    """Lấy chi tiết sản phẩm — **yêu cầu API key**."""
    product = next((p for p in _PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@app.get("/api/v1/search", tags=["API v1"])
def search(q: str, dev: dict = Depends(require_api_key)):
    """
    Tìm kiếm sản phẩm — **chỉ Pro & Enterprise**.

    Minh họa **feature gating**: tính năng premium bị chặn cho Free plan.
    """
    if dev["plan"] == "free":
        raise HTTPException(403, {
            "error":        "FEATURE_LOCKED",
            "message":      "Search API chỉ dành cho Pro và Enterprise.",
            "current_plan": "free",
            "upgrade_to":   "pro",
            "upgrade_url":  "POST /developers/upgrade",
            "pro_price":    "$29/tháng",
        })
    results = [p for p in _PRODUCTS if q.lower() in p["name"].lower()]
    return {"data": results, "query": q, "count": len(results)}


# ══════════════════════════════════════════════
# ADMIN ANALYTICS  (KPI Dashboard)
# ══════════════════════════════════════════════

@app.get("/admin/analytics", tags=["Admin"])
def admin_analytics(_: None = Depends(require_admin)):
    """
    **KPI Dashboard** — chỉ admin.

    Metrics: developer count · call volume · error rate · MRR · top endpoints.
    """
    return analytics.kpis()


@app.get("/admin/developers", tags=["Admin"])
def admin_developers(_: None = Depends(require_admin)):
    """Danh sách developers, usage và doanh thu mỗi account."""
    today = date.today().isoformat()
    rows  = []
    for dev in developers_db.values():
        rows.append({
            "email":         dev["email"],
            "name":          dev["name"],
            "plan":          dev["plan"],
            "created_at":    dev["created_at"],
            "calls_today":   dev["daily_usage"][today],
            "total_calls":   dev["total_calls"],
            "monthly_rev_usd": PLANS[dev["plan"]]["price_usd"],
        })
    rows.sort(key=lambda x: x["total_calls"], reverse=True)
    return {
        "total":      len(rows),
        "total_mrr":  sum(r["monthly_rev_usd"] for r in rows),
        "developers": rows,
    }
