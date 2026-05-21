"""
Buổi 10: Service Operation – Security & Monitoring
Demo: Hệ thống API có đầy đủ Logging, Metrics, Rate Limiting, Circuit Breaker, Audit Log

Chạy: py -m uvicorn main:app --reload
Docs: http://localhost:8000/docs
Metrics: http://localhost:8000/metrics
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
import time, json, logging, os, asyncio, random, uuid

# ══════════════════════════════════════════════
# 0. OPENTELEMETRY TRACING  (chỉ bật khi có OTEL_EXPORTER_OTLP_ENDPOINT)
# ══════════════════════════════════════════════

OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
if OTLP_ENDPOINT:
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        _provider = TracerProvider()
        _provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True))
        )
        trace.set_tracer_provider(_provider)
    except ImportError:
        pass  # OTel packages chưa cài — bỏ qua khi chạy local

# ══════════════════════════════════════════════
# 1. STRUCTURED LOGGING (thay Winston bằng Python)
# ══════════════════════════════════════════════

class JSONFormatter(logging.Formatter):
    """Format log thành JSON – chuẩn production (giống Winston)."""
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "payment-api",
            "module": record.module,
        }
        # Gắn thêm extra fields nếu có
        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)
        return json.dumps(log_entry, ensure_ascii=False)

# Tạo logger
logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

# Console handler – JSON format
console = logging.StreamHandler()
console.setFormatter(JSONFormatter())
logger.addHandler(console)

# File handler – ghi ra file log
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/api.log", encoding="utf-8")
file_handler.setFormatter(JSONFormatter())
logger.addHandler(file_handler)

# Audit logger riêng – ghi hành động nhạy cảm
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
audit_file = logging.FileHandler("logs/audit.log", encoding="utf-8")
audit_file.setFormatter(JSONFormatter())
audit_logger.addHandler(audit_file)


# ══════════════════════════════════════════════
# 2. PROMETHEUS METRICS (tự xây, không cần thư viện)
# ══════════════════════════════════════════════

class SimpleMetrics:
    """Bộ đếm metrics đơn giản mô phỏng Prometheus."""
    def __init__(self):
        self.request_count = defaultdict(int)      # {method_path: count}
        self.error_count = defaultdict(int)        # {method_path: count}
        self.latency_sum = defaultdict(float)       # {method_path: total_ms}
        self.latency_count = defaultdict(int)       # {method_path: count}
        self.rate_limit_hits = 0
        self.circuit_breaker_trips = 0
        self.start_time = time.time()

    def record_request(self, method: str, path: str, status: int, duration_ms: float):
        key = f'{method} {path}'
        self.request_count[key] += 1
        self.latency_sum[key] += duration_ms
        self.latency_count[key] += 1
        if status >= 400:
            self.error_count[key] += 1

    def to_prometheus_format(self) -> str:
        """Xuất metrics theo format Prometheus text."""
        lines = []
        lines.append("# HELP http_requests_total So luong request")
        lines.append("# TYPE http_requests_total counter")
        for key, count in self.request_count.items():
            method, path = key.split(" ", 1)
            lines.append(f'http_requests_total{{method="{method}",path="{path}"}} {count}')

        lines.append("\n# HELP http_errors_total So luong request loi")
        lines.append("# TYPE http_errors_total counter")
        for key, count in self.error_count.items():
            method, path = key.split(" ", 1)
            lines.append(f'http_errors_total{{method="{method}",path="{path}"}} {count}')

        lines.append("\n# HELP http_request_duration_ms Thoi gian xu ly trung binh (ms)")
        lines.append("# TYPE http_request_duration_ms gauge")
        for key in self.latency_sum:
            method, path = key.split(" ", 1)
            avg = self.latency_sum[key] / max(self.latency_count[key], 1)
            lines.append(f'http_request_duration_ms{{method="{method}",path="{path}"}} {avg:.2f}')

        lines.append(f"\n# HELP rate_limit_hits_total So lan bi rate limit")
        lines.append(f"# TYPE rate_limit_hits_total counter")
        lines.append(f"rate_limit_hits_total {self.rate_limit_hits}")

        lines.append(f"\n# HELP circuit_breaker_trips_total So lan circuit breaker mo")
        lines.append(f"# TYPE circuit_breaker_trips_total counter")
        lines.append(f"circuit_breaker_trips_total {self.circuit_breaker_trips}")

        uptime = time.time() - self.start_time
        lines.append(f"\n# HELP uptime_seconds Thoi gian server chay")
        lines.append(f"# TYPE uptime_seconds gauge")
        lines.append(f"uptime_seconds {uptime:.0f}")

        return "\n".join(lines) + "\n"

metrics = SimpleMetrics()


# ══════════════════════════════════════════════
# 3. RATE LIMITER (Sliding Window)
# ══════════════════════════════════════════════

class RateLimiter:
    """Rate limiter dùng Sliding Window – giới hạn request/phút theo IP."""
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> tuple[bool, dict]:
        now = time.time()
        window_start = now - self.window

        # Xóa request cũ ngoài cửa sổ
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if t > window_start
        ]

        remaining = self.max_requests - len(self.requests[client_ip])

        if remaining <= 0:
            return False, {
                "X-RateLimit-Limit": str(self.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(window_start + self.window)),
                "Retry-After": str(self.window),
            }

        self.requests[client_ip].append(now)
        return True, {
            "X-RateLimit-Limit": str(self.max_requests),
            "X-RateLimit-Remaining": str(remaining - 1),
        }

rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


# ══════════════════════════════════════════════
# 4. CIRCUIT BREAKER
# ══════════════════════════════════════════════

class CircuitBreaker:
    """
    Circuit Breaker pattern – bảo vệ hệ thống khi service bên ngoài lỗi.
    3 trạng thái: CLOSED (bình thường) → OPEN (chặn) → HALF_OPEN (thử lại)
    """
    def __init__(self, failure_threshold=3, recovery_timeout=15):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout  # giây
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            metrics.circuit_breaker_trips += 1
            logger.warning("Circuit Breaker OPEN - chan moi request den external service",
                extra={"extra_data": {"circuit_state": "OPEN", "failures": self.failure_count}})

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            # Kiểm tra đã hết thời gian recovery chưa
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit Breaker HALF_OPEN - thu lai 1 request",
                    extra={"extra_data": {"circuit_state": "HALF_OPEN"}})
                return True
            return False
        # HALF_OPEN: cho thử 1 request
        return True

circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=15)


# ══════════════════════════════════════════════
# 5. FASTAPI APP + MIDDLEWARE
# ══════════════════════════════════════════════

app = FastAPI(
    title="API Security & Monitoring Demo",
    description="Buoi 10: Logging, Metrics, Rate Limiting, Circuit Breaker",
    version="1.0.0",
)

# CORS – cho phép dashboard.html gọi API
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# OTel FastAPI instrumentation (tự động tạo span cho mọi request)
if OTLP_ENDPOINT:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)
    except ImportError:
        pass


# ── Middleware: Logging + Metrics + Security Headers ──

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start = time.time()
    client_ip = request.client.host if request.client else "unknown"

    # TRACING: Tạo hoặc nhận trace_id
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4())[:8])

    # Log request đến (kèm trace_id)
    logger.info(f"{request.method} {request.url.path}",
        extra={"extra_data": {
            "type": "request",
            "trace_id": trace_id,
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", ""),
        }})

    # Rate Limiting (bỏ qua /docs, /metrics, /openapi.json)
    skip_paths = ["/docs", "/metrics", "/openapi.json", "/redoc", "/health"]
    skip_prefixes = ("/api/external/", "/api/logs/")
    if request.url.path not in skip_paths and not request.url.path.startswith(skip_prefixes):
        allowed, rate_headers = rate_limiter.is_allowed(client_ip)
        if not allowed:
            metrics.rate_limit_hits += 1
            logger.warning(f"Rate limit exceeded for {client_ip}",
                extra={"extra_data": {"type": "rate_limit", "client_ip": client_ip}})
            resp = JSONResponse(
                status_code=429,
                content={"error": "TOO_MANY_REQUESTS", "message": f"Vuot qua {rate_limiter.max_requests} request/{rate_limiter.window}s. Vui long doi."}
            )
            for k, v in rate_headers.items():
                resp.headers[k] = v
            return resp

    response = await call_next(request)

    # Tính duration
    duration_ms = (time.time() - start) * 1000

    # Ghi metrics
    metrics.record_request(request.method, request.url.path, response.status_code, duration_ms)

    # Log response (kèm trace_id)
    logger.info(f"{response.status_code} {request.method} {request.url.path} ({duration_ms:.1f}ms)",
        extra={"extra_data": {
            "type": "response",
            "trace_id": trace_id,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "path": str(request.url.path),
        }})

    # TRACING: Trả trace_id về client qua header
    response.headers["X-Trace-ID"] = trace_id

    # Security Headers (WAF-like)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Rate limit headers
    is_rate_limited_path = (request.url.path not in skip_paths
                            and not request.url.path.startswith(skip_prefixes))
    if is_rate_limited_path and rate_limiter.requests.get(client_ip):
        remaining = rate_limiter.max_requests - len(rate_limiter.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))

    return response


# ══════════════════════════════════════════════
# API ENDPOINTS
# ══════════════════════════════════════════════

# ── Health Check ──
@app.get("/health", tags=["System"])
def health_check():
    """Endpoint kiểm tra sức khỏe server."""
    return {
        "status": "healthy",
        "uptime_seconds": int(time.time() - metrics.start_time),
        "circuit_breaker": circuit_breaker.state,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ── Prometheus Metrics ──
@app.get("/metrics", tags=["System"])
def get_metrics():
    """Endpoint xuất metrics theo format Prometheus."""
    return PlainTextResponse(
        content=metrics.to_prometheus_format(),
        media_type="text/plain",
    )


# ── CRUD Products (có audit log) ──

products_db = {
    1: {"id": 1, "name": "iPhone 16 Pro", "price": 28990000},
    2: {"id": 2, "name": "MacBook Air M3", "price": 27490000},
}
_next_id = 3

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, examples=["Galaxy S25"])
    price: int = Field(..., gt=0, examples=[22990000])

@app.get("/api/products", tags=["Products"])
def list_products():
    """Lấy danh sách sản phẩm."""
    return list(products_db.values())

@app.post("/api/products", status_code=201, tags=["Products"])
def create_product(body: ProductCreate, request: Request):
    """Tạo sản phẩm mới – có Audit Log."""
    global _next_id

    # WAF: Input sanitization đơn giản
    if "<script>" in body.name.lower():
        logger.warning("XSS attempt detected",
            extra={"extra_data": {"type": "security", "attack": "XSS", "input": body.name}})
        raise HTTPException(400, detail="Input khong hop le - phat hien ma doc")

    product = {"id": _next_id, "name": body.name, "price": body.price}
    products_db[_next_id] = product
    _next_id += 1

    # Audit Log – ghi hành động quan trọng
    audit_logger.info("PRODUCT_CREATED",
        extra={"extra_data": {
            "action": "CREATE",
            "resource": "product",
            "resource_id": product["id"],
            "data": product,
            "client_ip": request.client.host if request.client else "unknown",
        }})

    return product

@app.delete("/api/products/{product_id}", status_code=204, tags=["Products"])
def delete_product(product_id: int, request: Request):
    """Xóa sản phẩm – có Audit Log."""
    if product_id not in products_db:
        raise HTTPException(404, "Product not found")

    deleted = products_db.pop(product_id)

    # Audit Log
    audit_logger.info("PRODUCT_DELETED",
        extra={"extra_data": {
            "action": "DELETE",
            "resource": "product",
            "resource_id": product_id,
            "data": deleted,
            "client_ip": request.client.host if request.client else "unknown",
        }})


# ── External Service + Circuit Breaker ──

@app.get("/api/external/payment-gateway", tags=["Circuit Breaker"])
def call_payment_gateway():
    """
    Mô phỏng gọi dịch vụ thanh toán bên ngoài.
    60% thành công, 40% lỗi → kích hoạt Circuit Breaker sau 3 lần fail.
    """
    # Kiểm tra circuit breaker
    if not circuit_breaker.can_execute():
        return JSONResponse(
            status_code=503,
            content={
                "error": "CIRCUIT_OPEN",
                "message": f"Circuit Breaker dang MO. Service tam ngung {circuit_breaker.recovery_timeout}s.",
                "state": circuit_breaker.state,
                "retry_after": circuit_breaker.recovery_timeout,
            }
        )

    # Giả lập gọi external service (40% lỗi)
    if random.random() < 0.4:
        circuit_breaker.record_failure()
        logger.error("External payment gateway FAILED",
            extra={"extra_data": {
                "type": "circuit_breaker",
                "state": circuit_breaker.state,
                "failure_count": circuit_breaker.failure_count,
            }})
        raise HTTPException(502, detail={
            "error": "GATEWAY_ERROR",
            "message": "Payment gateway khong phan hoi",
            "circuit_state": circuit_breaker.state,
            "failures": f"{circuit_breaker.failure_count}/{circuit_breaker.failure_threshold}",
        })

    # Thành công
    circuit_breaker.record_success()
    return {
        "status": "success",
        "message": "Thanh toan thanh cong qua gateway",
        "circuit_state": circuit_breaker.state,
        "transaction_id": f"TXN-{random.randint(10000,99999)}",
    }


@app.get("/api/external/circuit-status", tags=["Circuit Breaker"])
def circuit_status():
    """Xem trạng thái hiện tại của Circuit Breaker."""
    return {
        "state": circuit_breaker.state,
        "failure_count": circuit_breaker.failure_count,
        "failure_threshold": circuit_breaker.failure_threshold,
        "recovery_timeout_seconds": circuit_breaker.recovery_timeout,
        "last_failure": datetime.fromtimestamp(circuit_breaker.last_failure_time).isoformat() if circuit_breaker.last_failure_time else None,
    }


@app.post("/api/external/circuit-reset", tags=["Circuit Breaker"])
def circuit_reset():
    """Reset Circuit Breaker về CLOSED (dùng khi demo)."""
    circuit_breaker.failure_count = 0
    circuit_breaker.state = "CLOSED"
    circuit_breaker.last_failure_time = None
    logger.info("Circuit Breaker RESET manually",
        extra={"extra_data": {"circuit_state": "CLOSED"}})
    return {"message": "Circuit Breaker da reset ve CLOSED", "state": "CLOSED"}


# ── Demo Rate Limit (endpoint riêng dễ test) ──

@app.get("/api/limited", tags=["Rate Limiting"])
def limited_endpoint():
    """Endpoint bị giới hạn 10 request/phút. Gọi quá → bị chặn 429."""
    return {
        "message": "Request thanh cong!",
        "note": "Endpoint nay bi gioi han 10 req/phut. Hay goi lien tuc de thu 429.",
    }


# ── Xem log file ──

@app.get("/api/logs/recent", tags=["System"])
def recent_logs(lines: int = 20):
    """Đọc N dòng log gần nhất từ file (demo cho lớp xem)."""
    try:
        with open("logs/api.log", "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        return {
            "total_lines": len(all_lines),
            "showing_last": min(lines, len(all_lines)),
            "logs": [json.loads(l) for l in all_lines[-lines:] if l.strip()],
        }
    except FileNotFoundError:
        return {"logs": [], "message": "Chua co log nao"}

@app.get("/api/logs/audit", tags=["System"])
def audit_logs(lines: int = 20):
    """Đọc N dòng audit log gần nhất."""
    try:
        with open("logs/audit.log", "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        return {
            "total_lines": len(all_lines),
            "logs": [json.loads(l) for l in all_lines[-lines:] if l.strip()],
        }
    except FileNotFoundError:
        return {"logs": [], "message": "Chua co audit log nao"}
