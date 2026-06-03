param(
    [string]$ProfileName = "online-boutique-lab",
    [string]$Namespace = "online-boutique",
    [string]$ManifestPath = "deploy/online-boutique/kubernetes-manifests.yaml",
    [string]$ImageListPath = "deploy/online-boutique/images.txt",
    [switch]$RestartPods
)

$ErrorActionPreference = "Continue"

if (-not (Test-Path $ManifestPath)) {
    Write-Host "Manifest file not found: $ManifestPath" -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path (Split-Path $ImageListPath -Parent) | Out-Null

$images = Select-String -Path $ManifestPath -Pattern "image:" |
    ForEach-Object { $_.Line.Trim() -replace "^image:\s*", "" } |
    Sort-Object -Unique

$images | Set-Content $ImageListPath -Encoding UTF8

Write-Host "Image list saved to: $ImageListPath" -ForegroundColor Cyan
Write-Host ""

$failedPull = @()
foreach ($image in $images) {
    Write-Host "Pulling $image" -ForegroundColor Cyan
    docker pull $image
    if ($LASTEXITCODE -ne 0) {
        $failedPull += $image
    }
}

if ($failedPull.Count -gt 0) {
    Write-Host ""
    Write-Host "Some images failed to pull from Windows Docker:" -ForegroundColor Red
    $failedPull | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    Write-Host "Check network or Docker Desktop proxy, then run this script again." -ForegroundColor Yellow
    exit 1
}

$failedLoad = @()
foreach ($image in $images) {
    Write-Host "Loading $image into Minikube profile $ProfileName" -ForegroundColor Green
    minikube image load $image -p $ProfileName
    if ($LASTEXITCODE -ne 0) {
        $failedLoad += $image
    }
}

if ($failedLoad.Count -gt 0) {
    Write-Host ""
    Write-Host "Some images failed to load into Minikube:" -ForegroundColor Red
    $failedLoad | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    exit 1
}

Write-Host ""
Write-Host "Images loaded into Minikube." -ForegroundColor Green

if ($RestartPods) {
    Write-Host "Restarting pods in namespace: $Namespace" -ForegroundColor Cyan
    kubectl delete pod --all -n $Namespace
    Write-Host "Use .\scripts\wait_online_boutique.ps1 to watch pod status."
}
