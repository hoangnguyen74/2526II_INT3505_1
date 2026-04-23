"""
Ví dụ Unit Test cho FastAPI bằng pytest + httpx
Chạy: py -m pytest test_unit.py -v
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── Test 1: Lấy danh sách sản phẩm ──────────────
def test_get_all_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1  # Phải có ít nhất 1 sản phẩm có sẵn


# ── Test 2: Tạo sản phẩm mới ────────────────────
def test_create_product():
    new_product = {"name": "Bàn phím cơ", "price": 1500000, "category": "Phụ kiện"}
    response = client.post("/products", json=new_product)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bàn phím cơ"
    assert "id" in data  # Server phải tự sinh ID


# ── Test 3: Lấy chi tiết sản phẩm ───────────────
def test_get_single_product():
    response = client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


# ── Test 4: Cập nhật sản phẩm ───────────────────
def test_update_product():
    response = client.put("/products/1", json={"price": 30000000})
    assert response.status_code == 200
    assert response.json()["price"] == 30000000


# ── Test 5: Sản phẩm không tồn tại → 404 ────────
def test_product_not_found():
    response = client.get("/products/9999")
    assert response.status_code == 404
