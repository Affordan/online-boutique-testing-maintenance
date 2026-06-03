# 构建、部署 coupon-service / inventory-service，并接入 frontend / checkout / productcatalog
param(
    [string]$MinikubeProfile = "online-boutique-lab",
    [string]$Namespace = "online-boutique"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

function Ensure-Command($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "Command not found: $name"
    }
}

Ensure-Command docker
Ensure-Command kubectl
Ensure-Command minikube

Write-Host "==> Build coupon-service image"
Push-Location "$RepoRoot\services\coupon-service"
docker build -t coupon-service:latest .
Pop-Location

Write-Host "==> Build inventory-service image"
Push-Location "$RepoRoot\services\inventory-service"
docker build -t inventory-service:latest .
Pop-Location

Write-Host "==> Load images into Minikube profile: $MinikubeProfile"
minikube -p $MinikubeProfile image load coupon-service:latest
minikube -p $MinikubeProfile image load inventory-service:latest

Write-Host "==> Deploy custom services"
kubectl apply -f "$RepoRoot\services\coupon-service\k8s" -n $Namespace
kubectl apply -f "$RepoRoot\services\inventory-service\k8s" -n $Namespace

Write-Host "==> Integrate env into frontend / checkoutservice / productcatalogservice"
kubectl apply -f "$RepoRoot\services\integration\k8s-env-integration.yaml" -n $Namespace

Write-Host "==> Wait for pods"
kubectl rollout status deployment/coupon-service -n $Namespace --timeout=120s
kubectl rollout status deployment/inventory-service -n $Namespace --timeout=120s

Write-Host "==> Done. Verify:"
Write-Host "kubectl get pods -n $Namespace | findstr coupon"
Write-Host "kubectl get pods -n $Namespace | findstr inventory"
Write-Host "kubectl port-forward svc/coupon-service 18081:8080 -n $Namespace"
Write-Host "curl http://localhost:18081/health"
