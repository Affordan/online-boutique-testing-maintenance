$ErrorActionPreference = "Continue"

function Test-Command {
    param(
        [string]$Name,
        [string]$Command
    )

    $exists = Get-Command $Command -ErrorAction SilentlyContinue
    if ($exists) {
        Write-Host "[OK] $Name" -ForegroundColor Green
        & $Command --version 2>$null
        Write-Host ""
    } else {
        Write-Host "[MISSING] $Name is not installed or not in PATH" -ForegroundColor Red
        Write-Host ""
    }
}

Write-Host "Checking local environment..." -ForegroundColor Cyan
Write-Host ""

Test-Command -Name "Docker" -Command "docker"
Test-Command -Name "kubectl" -Command "kubectl"
Test-Command -Name "Minikube" -Command "minikube"
Test-Command -Name "Helm" -Command "helm"
Test-Command -Name "Git" -Command "git"

$python = Get-Command python -ErrorAction SilentlyContinue
$python3 = Get-Command python3 -ErrorAction SilentlyContinue
if ($python) {
    Write-Host "[OK] Python" -ForegroundColor Green
    python --version
} elseif ($python3) {
    Write-Host "[OK] Python3" -ForegroundColor Green
    python3 --version
} else {
    Write-Host "[MISSING] Python is not installed or not in PATH" -ForegroundColor Red
}

Write-Host ""
Write-Host "Environment check finished." -ForegroundColor Cyan
