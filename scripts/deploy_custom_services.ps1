# 构建、部署 coupon-service / inventory-service，并用 kubectl set env 接入 Online-Boutique 既有服务。
param(
    [string]$MinikubeProfile = "online-boutique-lab",
    [string]$Namespace = "online-boutique"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

function Ensure-Command($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Command not found: $Name"
    }
}

function Invoke-Checked($CommandLine) {
    Write-Host "> $CommandLine" -ForegroundColor DarkGray
    cmd /c $CommandLine
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $CommandLine"
    }
}

Ensure-Command docker
Ensure-Command kubectl
Ensure-Command minikube

Write-Host "==> Verify Kubernetes context" -ForegroundColor Cyan
kubectl config use-context $MinikubeProfile
kubectl get namespace $Namespace | Out-Null

Write-Host "==> Build coupon-service image" -ForegroundColor Cyan
Invoke-Checked "docker build --pull=false -t coupon-service:latest `"$RepoRoot\services\coupon-service`""

Write-Host "==> Build inventory-service image" -ForegroundColor Cyan
Invoke-Checked "docker build --pull=false -t inventory-service:latest `"$RepoRoot\services\inventory-service`""

Write-Host "==> Load images into Minikube profile: $MinikubeProfile" -ForegroundColor Cyan
Invoke-Checked "minikube -p $MinikubeProfile image load coupon-service:latest"
Invoke-Checked "minikube -p $MinikubeProfile image load inventory-service:latest"

Write-Host "==> Deploy custom services" -ForegroundColor Cyan
kubectl apply -f "$RepoRoot\services\coupon-service\k8s" -n $Namespace
kubectl apply -f "$RepoRoot\services\inventory-service\k8s" -n $Namespace

Write-Host "==> Integrate custom service addresses into existing deployments" -ForegroundColor Cyan
kubectl set env deployment/frontend `
  COUPON_SERVICE_ADDR=http://coupon-service:8080 `
  INVENTORY_SERVICE_ADDR=http://inventory-service:8080 `
  -n $Namespace

kubectl set env deployment/checkoutservice `
  COUPON_SERVICE_ADDR=http://coupon-service:8080 `
  INVENTORY_SERVICE_ADDR=http://inventory-service:8080 `
  -n $Namespace

kubectl set env deployment/productcatalogservice `
  INVENTORY_SERVICE_ADDR=http://inventory-service:8080 `
  -n $Namespace

Write-Host "==> Wait for custom services" -ForegroundColor Cyan
kubectl rollout status deployment/coupon-service -n $Namespace --timeout=120s
kubectl rollout status deployment/inventory-service -n $Namespace --timeout=120s

Write-Host "==> Wait for integrated original services" -ForegroundColor Cyan
kubectl rollout status deployment/frontend -n $Namespace --timeout=180s
kubectl rollout status deployment/checkoutservice -n $Namespace --timeout=180s
kubectl rollout status deployment/productcatalogservice -n $Namespace --timeout=180s

Write-Host "==> Done. Verify:" -ForegroundColor Green
Write-Host "kubectl get pods -n $Namespace | findstr `"coupon inventory`""
Write-Host "kubectl get svc -n $Namespace | findstr `"coupon inventory`""
Write-Host "kubectl describe deployment frontend -n $Namespace | findstr `"COUPON INVENTORY`""
Write-Host "kubectl describe deployment checkoutservice -n $Namespace | findstr `"COUPON INVENTORY`""
Write-Host "kubectl describe deployment productcatalogservice -n $Namespace | findstr `"INVENTORY`""
