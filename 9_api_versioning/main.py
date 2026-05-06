"""
Buổi 9: API Versioning & Lifecycle Management
Demo: Hệ thống thanh toán (Payment API) phiên bản v1 → v2

Chạy: py -m uvicorn main:app --reload
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

app = FastAPI(
    title="Payment API - Demo Versioning",
    description="Minh hoạ 3 chiến lược versioning và case study nâng cấp v1 → v2",
    version="2.0.0",
)

# ══════════════════════════════════════════════
# CƠ SỞ DỮ LIỆU GIẢ LẬP
# ══════════════════════════════════════════════
payments_db: dict[str, dict] = {}


# ══════════════════════════════════════════════
# MIDDLEWARE: Gắn Deprecation Header cho v1
# ══════════════════════════════════════════════
@app.middleware("http")
async def deprecation_header(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path

    # Gắn header cảnh báo cho mọi request tới v1
    if "/api/v1/" in path:
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "2026-09-01T00:00:00Z"
        response.headers["Link"] = '</api/v2/payments>; rel="successor-version"'
        response.headers["X-Deprecation-Notice"] = (
            "API v1 se ngung ho tro tu 01/09/2026. "
            "Vui long chuyen sang /api/v2/. "
            "Xem huong dan: /api/migration-guide"
        )
    return response


# ══════════════════════════════════════════════════════
# CHIẾN LƯỢC 1: URL PATH VERSIONING  (/api/v1, /api/v2)
# ══════════════════════════════════════════════════════

# ── V1: PAYMENT API (Thiết kế cũ, có lỗi) ───────────

class PaymentV1Create(BaseModel):
    """Schema v1: amount là string, không có currency, card không mask."""
    amount: str = Field(..., examples=["50000"])
    card_number: str = Field(..., examples=["4111111111111111"])
    description: str = Field(default="", examples=["Thanh toan don hang"])


@app.post("/api/v1/payments", tags=["Strategy 1: URL Path - v1"])
def create_payment_v1(body: PaymentV1Create):
    """
    [DEPRECATED] Tạo thanh toán v1.
    ⚠️ Nhược điểm: amount là string dễ sai, card_number lộ, không có currency.
    """
    payment_id = str(uuid.uuid4())[:8]
    record = {
        "id": payment_id,
        "amount": body.amount,                # String → dễ gây lỗi so sánh
        "card_number": body.card_number,       # Lộ thông tin thẻ!
        "description": body.description,
        "status": "completed",
        "created_at": datetime.now().isoformat(),
    }
    payments_db[payment_id] = record
    return record


@app.get("/api/v1/payments", tags=["Strategy 1: URL Path - v1"])
def list_payments_v1():
    """[DEPRECATED] Trả về toàn bộ danh sách, không phân trang."""
    return list(payments_db.values())


@app.get("/api/v1/payments/{payment_id}", tags=["Strategy 1: URL Path - v1"])
def get_payment_v1(payment_id: str):
    """[DEPRECATED] Lấy chi tiết thanh toán v1."""
    if payment_id not in payments_db:
        raise HTTPException(404, "Payment not found")
    return payments_db[payment_id]


# ── V2: PAYMENT API (Thiết kế mới, sửa lỗi) ────────

class PaymentV2Create(BaseModel):
    """Schema v2: amount là integer (đơn vị xu), có currency, card bắt buộc mask."""
    amount: int = Field(..., gt=0, description="Số tiền tính bằng xu (VD: 5000000 = 50,000 VND)", examples=[5000000])
    currency: str = Field(default="VND", examples=["VND", "USD"])
    card_last4: str = Field(..., min_length=4, max_length=4, description="4 số cuối thẻ", examples=["1111"])
    description: str = Field(default="", examples=["Thanh toan don hang #1234"])
    idempotency_key: Optional[str] = Field(default=None, description="Chống gửi trùng", examples=["order-1234-abc"])


class PaymentV2Response(BaseModel):
    """Response wrapper chuẩn v2: luôn có data + meta."""
    data: dict
    meta: dict


@app.post("/api/v2/payments", response_model=PaymentV2Response, status_code=201, tags=["Strategy 1: URL Path - v2"])
def create_payment_v2(body: PaymentV2Create):
    """
    Tạo thanh toán v2.
    ✅ amount là integer, card đã mask, có currency, có idempotency_key.
    """
    # Chống gửi trùng
    if body.idempotency_key:
        for p in payments_db.values():
            if p.get("idempotency_key") == body.idempotency_key:
                return PaymentV2Response(
                    data=p,
                    meta={"duplicate": True, "message": "Request da duoc xu ly truoc do"}
                )

    payment_id = str(uuid.uuid4())[:8]
    record = {
        "id": payment_id,
        "amount": body.amount,
        "currency": body.currency,
        "card": f"****-****-****-{body.card_last4}",   # Đã che số thẻ
        "description": body.description,
        "idempotency_key": body.idempotency_key,
        "status": "completed",
        "created_at": datetime.now().isoformat(),
    }
    payments_db[payment_id] = record
    return PaymentV2Response(
        data=record,
        meta={"api_version": "v2"}
    )


@app.get("/api/v2/payments", tags=["Strategy 1: URL Path - v2"])
def list_payments_v2(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=50)):
    """Danh sách thanh toán v2 — có phân trang."""
    all_items = list(payments_db.values())
    start = (page - 1) * limit
    items = all_items[start:start + limit]
    return {
        "data": items,
        "meta": {
            "page": page,
            "limit": limit,
            "total": len(all_items),
            "api_version": "v2",
        }
    }


@app.get("/api/v2/payments/{payment_id}", tags=["Strategy 1: URL Path - v2"])
def get_payment_v2(payment_id: str):
    """Lấy chi tiết thanh toán v2 — response bọc trong data."""
    if payment_id not in payments_db:
        raise HTTPException(404, detail={"error": "PAYMENT_NOT_FOUND", "message": f"Khong tim thay ID={payment_id}"})
    return {"data": payments_db[payment_id], "meta": {"api_version": "v2"}}


# ══════════════════════════════════════════════════════
# CHIẾN LƯỢC 2: HEADER VERSIONING (Accept / Custom Header)
# ══════════════════════════════════════════════════════

@app.get("/api/products", tags=["Strategy 2: Header Versioning"])
def get_products_header(
    x_api_version: str = Header(default="1", alias="X-API-Version")
):
    """
    Cùng 1 URL, phân biệt version qua header X-API-Version.
    - X-API-Version: 1 → trả response cũ (mảng phẳng)
    - X-API-Version: 2 → trả response mới (bọc data + meta)
    """
    products = [
        {"id": 1, "name": "iPhone 16", "price": 28990000},
        {"id": 2, "name": "Galaxy S25", "price": 22990000},
    ]

    if x_api_version == "2":
        return {
            "data": products,
            "meta": {"api_version": "v2", "total": len(products)}
        }
    else:
        # v1: trả mảng thô
        return products


# ══════════════════════════════════════════════════════
# CHIẾN LƯỢC 3: QUERY PARAMETER VERSIONING
# ══════════════════════════════════════════════════════

@app.get("/api/orders", tags=["Strategy 3: Query Param Versioning"])
def get_orders_query(version: str = Query("1")):
    """
    Phân biệt version qua query ?version=1 hoặc ?version=2.
    - ?version=1 → format cũ
    - ?version=2 → format mới
    """
    orders = [
        {"id": "ORD-001", "total": 150000, "items": 3},
        {"id": "ORD-002", "total": 89000, "items": 1},
    ]

    if version == "2":
        return {
            "data": [
                {**o, "total_formatted": f"{o['total']:,} VND"} for o in orders
            ],
            "meta": {"api_version": "v2"}
        }
    else:
        return orders


# ══════════════════════════════════════════════════════
# TRANG MIGRATION GUIDE (trả JSON)
# ══════════════════════════════════════════════════════

@app.get("/api/migration-guide", tags=["Lifecycle"])
def migration_guide():
    """Hướng dẫn chuyển đổi từ v1 sang v2 cho developers."""
    return {
        "title": "Huong dan chuyen doi API v1 → v2",
        "deadline": "2026-09-01",
        "breaking_changes": [
            {
                "field": "amount",
                "v1": "string ('50000')",
                "v2": "integer (5000000 = 50,000 VND tinh bang xu)",
                "action": "Chuyen doi string → int, nhan voi 100"
            },
            {
                "field": "card_number → card_last4",
                "v1": "Gui ca so the day du (16 so)",
                "v2": "Chi gui 4 so cuoi (VD: '1111')",
                "action": "Cat chuoi, chi lay 4 ky tu cuoi"
            },
            {
                "field": "currency (MOI)",
                "v1": "Khong co",
                "v2": "Bat buoc, mac dinh 'VND'",
                "action": "Them truong currency vao request body"
            },
            {
                "field": "Response format",
                "v1": "Tra truc tiep object: {id, amount, ...}",
                "v2": "Boc trong wrapper: {data: {...}, meta: {...}}",
                "action": "Doc response.data thay vi response truc tiep"
            },
        ],
        "timeline": [
            {"date": "2026-05-01", "event": "v2 ra mat, v1 van hoat dong binh thuong"},
            {"date": "2026-07-01", "event": "v1 bat dau tra header Deprecation + Sunset"},
            {"date": "2026-08-01", "event": "v1 gioi han rate limit xuong 10 req/phut"},
            {"date": "2026-09-01", "event": "v1 ngung hoat dong, tra 410 Gone"},
        ]
    }
