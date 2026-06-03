param(
    [string]$TargetPath = "deploy/online-boutique/kubernetes-manifests.yaml"
)

$ErrorActionPreference = "Stop"

$target = Join-Path (Get-Location) $TargetPath
$targetDir = Split-Path $target -Parent
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

$primary = "https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml"
$fallback = "https://raw.githubusercontent.com/JoinFyc/Online-Boutique/release/v0.10.2/release/kubernetes-manifests.yaml"

Write-Host "Downloading Online-Boutique Kubernetes manifest..." -ForegroundColor Cyan
Write-Host "Target: $target"

try {
    Invoke-WebRequest -Uri $primary -OutFile $target -UseBasicParsing
    Write-Host "Downloaded from primary source." -ForegroundColor Green
} catch {
    Write-Host "Primary source failed. Trying fallback source..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $fallback -OutFile $target -UseBasicParsing
    Write-Host "Downloaded from fallback source." -ForegroundColor Green
}

$sizeKB = [Math]::Round((Get-Item $target).Length / 1KB, 2)
Write-Host "Manifest saved. Size: $sizeKB KB" -ForegroundColor Green
