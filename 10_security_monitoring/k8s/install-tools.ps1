# install-tools.ps1
# Cài minikube, kubectl, helm vào D:\tools\ (không cần admin)
# Chạy: PowerShell -ExecutionPolicy Bypass -File install-tools.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$toolsDir = "D:\tools"
New-Item -ItemType Directory -Force $toolsDir | Out-Null
Write-Host "`n[1/4] Thu muc: $toolsDir" -ForegroundColor Cyan

# ── minikube ──
Write-Host "[2/4] Tai minikube..." -ForegroundColor Cyan
$mkUrl = "https://storage.googleapis.com/minikube/releases/latest/minikube-windows-amd64.exe"
Invoke-WebRequest -Uri $mkUrl -OutFile "$toolsDir\minikube.exe" -UseBasicParsing
Write-Host "      OK: $toolsDir\minikube.exe" -ForegroundColor Green

# ── kubectl ──
Write-Host "[3/4] Tai kubectl..." -ForegroundColor Cyan
$k8sVer = "v1.30.2"
$kubUrl  = "https://dl.k8s.io/release/$k8sVer/bin/windows/amd64/kubectl.exe"
Invoke-WebRequest -Uri $kubUrl -OutFile "$toolsDir\kubectl.exe" -UseBasicParsing
Write-Host "      OK: $toolsDir\kubectl.exe" -ForegroundColor Green

# ── helm ──
Write-Host "[4/4] Tai helm..." -ForegroundColor Cyan
$helmVer = "v3.15.2"
$helmUrl = "https://get.helm.sh/helm-$helmVer-windows-amd64.zip"
$helmZip = "$toolsDir\helm.zip"
Invoke-WebRequest -Uri $helmUrl -OutFile $helmZip -UseBasicParsing
Expand-Archive -Path $helmZip -DestinationPath "$toolsDir\helm-tmp" -Force
Move-Item "$toolsDir\helm-tmp\windows-amd64\helm.exe" "$toolsDir\helm.exe" -Force
Remove-Item "$toolsDir\helm-tmp" -Recurse -Force
Remove-Item $helmZip -Force
Write-Host "      OK: $toolsDir\helm.exe" -ForegroundColor Green

# ── MINIKUBE_HOME → D:\minikube ──
Write-Host "`nCau hinh MINIKUBE_HOME = D:\minikube" -ForegroundColor Cyan
[System.Environment]::SetEnvironmentVariable("MINIKUBE_HOME", "D:\minikube", "User")
$env:MINIKUBE_HOME = "D:\minikube"
New-Item -ItemType Directory -Force "D:\minikube" | Out-Null

# ── Them D:\tools vao PATH (User) ──
$currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*D:\tools*") {
    [System.Environment]::SetEnvironmentVariable("PATH", "$currentPath;$toolsDir", "User")
    Write-Host "Da them D:\tools vao PATH (User)" -ForegroundColor Green
} else {
    Write-Host "D:\tools da co trong PATH" -ForegroundColor Yellow
}

Write-Host "`n[OK] Hoan thanh! Mo terminal moi va kiem tra:" -ForegroundColor Green
Write-Host "  minikube version"
Write-Host "  kubectl version --client"
Write-Host "  helm version"
Write-Host ""
Write-Host "Buoc tiep theo: Cai Docker Desktop, sau do chay start-cluster.ps1" -ForegroundColor Yellow
