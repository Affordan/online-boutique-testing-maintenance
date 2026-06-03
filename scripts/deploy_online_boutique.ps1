param(
    [string]$Namespace = "online-boutique",
    [string]$ManifestPath = "deploy/online-boutique/kubernetes-manifests.yaml"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ManifestPath)) {
    Write-Host "Manifest file not found: $ManifestPath" -ForegroundColor Red
    Write-Host "Run: .\scripts\download_online_boutique_manifest.ps1"
    exit 1
}

Write-Host "Current kubectl context:" -ForegroundColor Cyan
kubectl config current-context

Write-Host ""
Write-Host "Creating namespace: $Namespace" -ForegroundColor Cyan
kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -

Write-Host ""
Write-Host "Applying Online-Boutique manifest..." -ForegroundColor Cyan
kubectl apply -f $ManifestPath -n $Namespace

Write-Host ""
Write-Host "Deployment submitted." -ForegroundColor Green

Write-Host ""
Write-Host "Pods:" -ForegroundColor Cyan
kubectl get pods -n $Namespace

Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
kubectl get svc -n $Namespace
