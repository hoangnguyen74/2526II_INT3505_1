"""
Demo API Testing - FastAPI Product Management
Buổi 8: API Testing và Quality Assurance

Server này cung cấp 5 endpoints CRUD cho tài nguyên "Product":
  GET    /products         - Lấy danh sách
  POST   /products         - Tạo mới
  GET    /products/{id}    - Lấy chi tiết
  PUT    /products/{id}    - Cập nhật
  DELETE /products/{id}    - Xoá

Chạy: py -m uvicorn main:app --reload
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import time, random

app = FastAPI(
    title="Product API - Demo Buổi 8",
    description="API quản lý sản phẩm phục vụ bài giảng API Testing & QA",
    version="1.0.0",
)

# ──────────────────────────────────────────────
# Cơ sở dữ liệu giả lập (In-memory)
# ──────────────────────────────────────────────
products_db: dict[int, dict] = {
    1: {"id": 1, "name": "iPhone 16 Pro", "price": 28990000, "category": "Điện thoại"},
    2: {"id": 2, "name": "MacBook Air M3", "price": 27490000, "category": "Laptop"},
    3: {"id": 3, "name": "AirPods Pro 2", "price": 5990000, "category": "Phụ kiện"},
}
_next_id = 4


# ──────────────────────────────────────────────
# Pydantic Models (Request/Response schemas)
# ──────────────────────────────────────────────
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, examples=["Galaxy S25"])
    price: int = Field(..., gt=0, examples=[22990000])
    category: str = Field(default="Chưa phân loại", examples=["Điện thoại"])


class ProductUpdate(BaseModel):
    name: str | None = None
    price: int | None = Field(default=None, gt=0)
    category: str | None = None


# ──────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────

@app.get("/products", tags=["Products"])
def list_products():
    """Trả về danh sách toàn bộ sản phẩm."""
    return list(products_db.values())


@app.post("/products", status_code=201, tags=["Products"])
def create_product(body: ProductCreate):
    """Tạo sản phẩm mới, trả về sản phẩm vừa tạo kèm ID."""
    global _next_id
    product = {"id": _next_id, **body.model_dump()}
    products_db[_next_id] = product
    _next_id += 1
    return product


@app.get("/products/{product_id}", tags=["Products"])
def get_product(product_id: int):
    """Trả về chi tiết 1 sản phẩm theo ID."""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm ID={product_id}")
    return products_db[product_id]


@app.put("/products/{product_id}", tags=["Products"])
def update_product(product_id: int, body: ProductUpdate):
    """Cập nhật thông tin sản phẩm (partial update)."""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm ID={product_id}")
    for key, value in body.model_dump(exclude_unset=True).items():
        products_db[product_id][key] = value
    return products_db[product_id]


@app.delete("/products/{product_id}", status_code=204, tags=["Products"])
def delete_product(product_id: int):
    """Xoá sản phẩm khỏi cửa hàng."""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm ID={product_id}")
    del products_db[product_id]


# ──────────────────────────────────────────────
# Endpoint đặc biệt: Mô phỏng API chậm/lỗi
# Dùng để demo Load Testing - thấy rõ Error Rate
# ──────────────────────────────────────────────
@app.get("/products/heavy/report", tags=["Performance Demo"])
def heavy_report():
    """
    Endpoint cố tình chạy chậm (0.5-2s) và ngẫu nhiên trả lỗi 500.
    Mục đích: Khi chạy Load Test, biểu đồ sẽ hiện rõ
    Response Time tăng vọt và Error Rate nhảy đỏ.
    """
    time.sleep(random.uniform(0.5, 2.0))
    if random.random() < 0.3:  # 30% xác suất lỗi
        raise HTTPException(status_code=500, detail="Database timeout (lỗi giả lập)")
    return {"status": "ok", "generated_at": time.time()}
