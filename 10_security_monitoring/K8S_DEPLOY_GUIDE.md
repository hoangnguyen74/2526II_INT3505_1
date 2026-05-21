# Buổi 10: Deploy lên Kubernetes — Hướng dẫn đầy đủ

## Kiến trúc

```
Minikube (local K8s)  ─── namespace: monitoring
│
├── payment-api  ×2 replicas
│   ├── stdout JSON logs ──────────► Promtail ──► Loki
│   ├── GET /metrics (Prometheus fmt) ◄── Prometheus scrape
│   └── OTel spans ────────────────────────────► Jaeger
│
├── Prometheus   → thu thập metrics
├── Grafana      → visualize (Prometheus + Loki + Jaeger)
├── Loki         → log aggregation
├── Promtail     → thu thập stdout logs từ pods
└── Jaeger       → distributed tracing UI
```

---

## Bước 1 — Cài đặt tools (chỉ làm một lần)

### 1a. Docker Desktop
1. Tải: https://docs.docker.com/desktop/install/windows-install/
2. Cài đặt (vào `C:\Program Files\Docker` — không tránh được)
3. Mở Docker Desktop → Settings → Resources → Advanced
   - **Disk image location**: đổi thành `D:\DockerData`
   - Apply & Restart
4. Di chuyển WSL data sang D drive (tùy chọn, tiết kiệm C drive):
```powershell
wsl --shutdown
wsl --export docker-desktop-data D:\DockerData\dd-data.tar
wsl --unregister docker-desktop-data
wsl --import docker-desktop-data D:\DockerData\wsl D:\DockerData\dd-data.tar --version 2
```

### 1b. minikube + kubectl + helm → D:\tools\
```powershell
# Chạy script có sẵn (tự động download và cấu hình)
PowerShell -ExecutionPolicy Bypass -File k8s\install-tools.ps1
```
Sau đó **mở terminal mới** (để PATH có hiệu lực) và kiểm tra:
```powershell
minikube version   # minikube version: v1.33.x
kubectl version --client
helm version
```

---

## Bước 2 — Khởi động cluster (mỗi lần dùng)

```powershell
cd 10_security_monitoring

# Chạy một lệnh duy nhất — tự động làm tất cả
PowerShell -ExecutionPolicy Bypass -File k8s\start-cluster.ps1
```

Script này sẽ:
1. Kiểm tra Docker đang chạy
2. Start Minikube (4GB RAM, 2 CPU)
3. Build Docker image `payment-api:latest`
4. Deploy app lên namespace `monitoring`
5. Cài Prometheus + Grafana qua Helm
6. Cài Loki + Promtail qua Helm
7. Deploy Jaeger all-in-one
8. Đợi pods sẵn sàng rồi in thông tin truy cập

> ⏱ Lần đầu chạy mất **5–10 phút** (pull Docker images). Các lần sau ~1 phút.

---

## Bước 3 — Truy cập services

Mở **4 terminal** (hoặc dùng Windows Terminal tabs), mỗi terminal chạy một port-forward:

```powershell
# Terminal 1 — App
kubectl port-forward svc/payment-api 8000:8000 -n monitoring
# → http://localhost:8000/docs

# Terminal 2 — Grafana
kubectl port-forward svc/kube-prom-grafana 3000:80 -n monitoring
# → http://localhost:3000  (login: admin / admin123)

# Terminal 3 — Jaeger UI
kubectl port-forward svc/jaeger-query 16686:16686 -n monitoring
# → http://localhost:16686

# Terminal 4 — Prometheus (tùy chọn)
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring
# → http://localhost:9090
```

---

## Bước 4 — Demo trong lớp

### 4.1 Xem logs real-time
```powershell
# Stream logs từ cả 2 replicas
kubectl logs -l app=payment-api -n monitoring -f

# Sau đó gọi API → thấy JSON logs
curl http://localhost:8000/api/products
```

**Trong Grafana**: Explore → Loki → `{app="payment-api"}` → thấy logs realtime

---

### 4.2 Xem metrics trong Grafana

1. Grafana → Dashboards → **FastAPI Observability** (auto-import)
2. Hoặc Explore → Prometheus → query:
   - `http_requests_total{app="payment-api"}` — tổng requests
   - `http_request_duration_ms{app="payment-api"}` — latency
   - `rate_limit_hits_total` — số lần bị rate limit

Tạo traffic:
```powershell
# Gọi 20 requests để có data
for ($i=1; $i -le 20; $i++) { curl http://localhost:8000/api/products }
```

---

### 4.3 Demo Rate Limiting (429)
```powershell
# Gọi 15 lần nhanh → lần 11 sẽ bị 429
for ($i=1; $i -le 15; $i++) {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/api/limited" -ErrorAction SilentlyContinue
    Write-Host "$i → $($r.StatusCode)"
}
```
**Grafana**: `rate_limit_hits_total` tăng lên.

---

### 4.4 Demo Circuit Breaker
```powershell
# Gọi liên tục → sau 3 lần fail, circuit OPEN → 503
for ($i=1; $i -le 10; $i++) {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/api/external/payment-gateway" -ErrorAction SilentlyContinue
    Write-Host "$i → $($r.StatusCode) $(($r.Content | ConvertFrom-Json).circuit_state)"
}
# Xem circuit status
curl http://localhost:8000/api/external/circuit-status
```

---

### 4.5 Xem Distributed Tracing (Jaeger)
1. Mở http://localhost:16686
2. Service: `payment-api`
3. Click **Find Traces**
4. Click vào một trace → thấy các spans của request

> **Lưu ý**: Traces chỉ hiện nếu biến môi trường `OTEL_EXPORTER_OTLP_ENDPOINT` được set trong deployment.yaml. Kiểm tra bằng `kubectl describe pod -l app=payment-api -n monitoring`.

---

### 4.6 Xem Kubernetes dashboard
```powershell
minikube dashboard
# Tự động mở browser với K8s Dashboard
```

---

## Dừng cluster (cuối buổi)
```powershell
minikube stop       # dừng cluster, giữ nguyên state
# hoặc
minikube delete     # xóa hoàn toàn (lần sau cần chạy lại start-cluster.ps1)
```

---

## Troubleshooting

| Vấn đề | Kiểm tra | Giải pháp |
|--------|---------|-----------|
| Pod `CrashLoopBackOff` | `kubectl describe pod -n monitoring` | Xem Events ở cuối output |
| Pod `ImagePullBackOff` | `kubectl describe pod -n monitoring` | Build lại image: `minikube image build -t payment-api:latest .` |
| Helm timeout | `kubectl get pods -n monitoring` | Tăng `--timeout 10m` trong start-cluster.ps1 |
| Không thấy traces | `kubectl describe pod -l app=payment-api -n monitoring` | Kiểm tra env OTEL_EXPORTER_OTLP_ENDPOINT |
| Loki không có logs | `kubectl logs -l app.kubernetes.io/name=promtail -n monitoring` | Xem Promtail errors |

```powershell
# Xem tất cả pods
kubectl get pods -n monitoring

# Xem log của pod cụ thể
kubectl logs <pod-name> -n monitoring

# Xem events
kubectl get events -n monitoring --sort-by='.lastTimestamp'
```

---

## Cấu trúc files

```
10_security_monitoring/
├── main.py                          # FastAPI app (đã thêm OTel)
├── requirements.txt                 # Đã thêm opentelemetry packages
├── Dockerfile                       # Container image
├── K8S_DEPLOY_GUIDE.md              # File này
└── k8s/
    ├── install-tools.ps1            # Cài minikube/kubectl/helm → D:\tools\
    ├── start-cluster.ps1            # Khởi động toàn bộ stack
    ├── namespace.yaml               # K8s namespace: monitoring
    ├── app/
    │   ├── deployment.yaml          # App deployment (2 replicas + OTel env)
    │   └── service.yaml             # ClusterIP service
    ├── prometheus/
    │   └── helm-values.yaml         # Prometheus + Grafana config
    ├── loki/
    │   └── helm-values.yaml         # Loki + Promtail config
    └── jaeger/
        └── jaeger.yaml              # Jaeger all-in-one manifest
```
