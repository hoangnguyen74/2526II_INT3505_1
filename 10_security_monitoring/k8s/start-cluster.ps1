# start-cluster.ps1
# Khoi dong Minikube va deploy toan bo stack
# Yeu cau: Docker Desktop dang chay, MINIKUBE_HOME=D:\minikube
# Chay: PowerShell -ExecutionPolicy Bypass -File start-cluster.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$rootDir = Split-Path $PSScriptRoot -Parent   # 10_security_monitoring/

function Step($msg) { Write-Host "`n==[ $msg ]==" -ForegroundColor Cyan }
function OK($msg)   { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "  ! $msg" -ForegroundColor Yellow }

# ── 1. Kiem tra Docker dang chay ──
Step "Kiem tra Docker"
docker info | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker chua chay! Mo Docker Desktop truoc." -ForegroundColor Red
    exit 1
}
OK "Docker dang chay"

# ── 2. Start Minikube ──
Step "Start Minikube (4GB RAM, 2 CPU)"
$mkStatus = minikube status --format='{{.Host}}' 2>$null
if ($mkStatus -eq "Running") {
    OK "Minikube da chay san"
} else {
    minikube start --driver=docker --memory=4096 --cpus=2 --disk-size=20g
    OK "Minikube da khoi dong"
}

# ── 3. Build Docker image vao minikube ──
Step "Build image payment-api:latest"
minikube image build -t payment-api:latest $rootDir
OK "Image da build"

# ── 4. Deploy namespace + app ──
Step "Deploy namespace va app"
kubectl apply -f "$PSScriptRoot\namespace.yaml"
kubectl apply -f "$PSScriptRoot\app\"
OK "App deployed"

# ── 5. Helm repos ──
Step "Them Helm repos"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>$null
helm repo add grafana https://grafana.github.io/helm-charts 2>$null
helm repo update
OK "Helm repos updated"

# ── 6. Prometheus + Grafana ──
Step "Deploy Prometheus + Grafana (kube-prometheus-stack)"
$promExists = helm list -n monitoring --short | Select-String "kube-prom"
if ($promExists) {
    Warn "kube-prom da ton tai, bo qua"
} else {
    helm install kube-prom prometheus-community/kube-prometheus-stack `
        -f "$PSScriptRoot\prometheus\helm-values.yaml" `
        -n monitoring --timeout 5m
    OK "Prometheus + Grafana deployed"
}

# ── 7. Loki + Promtail ──
Step "Deploy Loki + Promtail"
$lokiExists = helm list -n monitoring --short | Select-String "^loki$"
if ($lokiExists) {
    Warn "loki da ton tai, bo qua"
} else {
    helm install loki grafana/loki-stack `
        -f "$PSScriptRoot\loki\helm-values.yaml" `
        -n monitoring --timeout 5m
    OK "Loki + Promtail deployed"
}

# ── 8. Jaeger ──
Step "Deploy Jaeger all-in-one"
kubectl apply -f "$PSScriptRoot\jaeger\jaeger.yaml"
OK "Jaeger deployed"

# ── 9. Cho pods san sang ──
Step "Doi pods san sang (co the mat 2-3 phut)"
kubectl wait --for=condition=ready pod -l app=payment-api -n monitoring --timeout=120s
OK "payment-api pods Ready"

# ── 10. In thong tin truy cap ──
Write-Host "`n" + "="*60 -ForegroundColor Green
Write-Host "STACK DA CHAY! Port-forward de truy cap:" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green
Write-Host ""
Write-Host "App API    : kubectl port-forward svc/payment-api 8000:8000 -n monitoring"
Write-Host "             → http://localhost:8000/docs"
Write-Host ""
Write-Host "Grafana    : kubectl port-forward svc/kube-prom-grafana 3000:80 -n monitoring"
Write-Host "             → http://localhost:3000  (admin / admin123)"
Write-Host ""
Write-Host "Jaeger UI  : kubectl port-forward svc/jaeger-query 16686:16686 -n monitoring"
Write-Host "             → http://localhost:16686"
Write-Host ""
Write-Host "Prometheus : kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring"
Write-Host "             → http://localhost:9090"
Write-Host ""
Write-Host "Xem logs   : kubectl logs -l app=payment-api -n monitoring -f"
Write-Host "Xem pods   : kubectl get pods -n monitoring"
