param(
    [string]$OutputPath = "deploy\online-boutique\kubernetes-manifests.yaml"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Target = Join-Path $RepoRoot $OutputPath
$TargetDir = Split-Path -Parent $Target
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

$PrimaryUrl = "https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml"
$FallbackUrl = "https://raw.githubusercontent.com/JoinFyc/Online-Boutique/release/v0.10.2/release/kubernetes-manifests.yaml"

Write-Host "Downloading Online-Boutique Kubernetes manifest..." -ForegroundColor Cyan
Write-Host "Target: $Target"

try {
    Invoke-WebRequest -Uri $PrimaryUrl -OutFile $Target -UseBasicParsing -TimeoutSec 60
    Write-Host "Downloaded from primary source." -ForegroundColor Green
} catch {
    Write-Host "Primary source failed. Trying fallback source..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $FallbackUrl -OutFile $Target -UseBasicParsing -TimeoutSec 60
    Write-Host "Downloaded from fallback source." -ForegroundColor Green
}

$SizeKB = [Math]::Round((Get-Item $Target).Length / 1KB, 2)
Write-Host "Manifest saved. Size: $SizeKB KB" -ForegroundColor Green
