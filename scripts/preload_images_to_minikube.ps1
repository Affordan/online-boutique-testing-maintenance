param(
    [string]$ProfileName = "online-boutique-lab",
    [string]$Namespace = "online-boutique",
    [string]$ManifestPath = "deploy\online-boutique\kubernetes-manifests.yaml",
    [switch]$RestartPods
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Manifest = Join-Path $RepoRoot $ManifestPath
$ImageList = Join-Path (Split-Path -Parent $Manifest) "images.txt"

if (-not (Test-Path $Manifest)) { throw "Manifest not found: $Manifest" }

Write-Host "Extracting images from manifest..." -ForegroundColor Cyan
$images = Select-String -Path $Manifest -Pattern "image:" |
    ForEach-Object { $_.Line.Trim().Replace("image:", "").Trim() } |
    Sort-Object -Unique
$images | Set-Content $ImageList

Write-Host "Images:" -ForegroundColor Cyan
$images | ForEach-Object { Write-Host "  $_" }

foreach ($img in $images) {
    Write-Host "Pulling $img" -ForegroundColor Cyan
    docker pull $img
    if ($LASTEXITCODE -ne 0) { throw "docker pull failed: $img" }
}

foreach ($img in $images) {
    Write-Host "Loading $img into Minikube profile: $ProfileName" -ForegroundColor Green
    minikube -p $ProfileName image load $img
    if ($LASTEXITCODE -ne 0) { throw "minikube image load failed: $img" }
}

if ($RestartPods) {
    Write-Host "Restarting pods in namespace: $Namespace" -ForegroundColor Yellow
    kubectl delete pod --all -n $Namespace
}

Write-Host "Image preload finished." -ForegroundColor Green
