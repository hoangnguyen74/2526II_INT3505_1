"""
Load Testing với Locust - Buổi 8

Chạy:  locust
Mở:    http://localhost:8089
Điền:  Host = http://localhost:8000, Users = 50, Spawn rate = 5
"""

from locust import HttpUser, task, between


class ProductAPIUser(HttpUser):
    """Mô phỏng 1 người dùng thật tương tác với API."""

    wait_time = between(0.5, 1.5)  # Thời gian nghỉ giữa các request

    @task(5)
    def browse_products(self):
        """Hành vi phổ biến nhất: Xem danh sách sản phẩm."""
        self.client.get("/products")

    @task(3)
    def view_detail(self):
        """Xem chi tiết 1 sản phẩm."""
        self.client.get("/products/1")

    @task(1)
    def create_product(self):
        """Thỉnh thoảng tạo sản phẩm mới."""
        self.client.post("/products", json={
            "name": "Sản phẩm Load Test",
            "price": 100000,
            "category": "Test"
        })

    @task(2)
    def hit_heavy_endpoint(self):
        """
        Đâm vào endpoint cố tình chậm/lỗi.
        → Biểu đồ Locust sẽ hiện Error Rate tăng + Response Time vọt lên.
        """
        with self.client.get("/products/heavy/report", catch_response=True) as resp:
            if resp.status_code == 500:
                resp.failure("Server trả lỗi 500 (giả lập timeout)")
