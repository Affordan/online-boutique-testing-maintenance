param(
    [string]$Namespace = "online-boutique",
    [string]$ManifestPath = "deploy\online-boutique\kubernetes-manifests.yaml"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Manifest = Join-Path $RepoRoot $ManifestPath

if (-not (Test-Path $Manifest)) {
    throw "Manifest not found: $Manifest. Run .\scripts\download_online_boutique_manifest.ps1 first."
}

Write-Host "Creating namespace: $Namespace" -ForegroundColor Cyan
kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -

Write-Host "Deploying Online-Boutique..." -ForegroundColor Cyan
kubectl apply -f $Manifest -n $Namespace

Write-Host "Deployment submitted." -ForegroundColor Green
Write-Host ""
Write-Host "Pods:" -ForegroundColor Cyan
kubectl get pods -n $Namespace
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
kubectl get svc -n $Namespace
