$ErrorActionPreference = "Continue"

function Test-Command($Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $cmd) {
        Write-Host "[MISSING] $Name is not installed or not in PATH" -ForegroundColor Red
        return $false
    }
    Write-Host "[OK] $Name" -ForegroundColor Green
    & $Name --version 2>$null
    return $true
}

Write-Host "Checking environment..." -ForegroundColor Cyan
Write-Host ""

Test-Command docker | Out-Null
Write-Host ""
Test-Command kubectl | Out-Null
Write-Host ""
Test-Command minikube | Out-Null
Write-Host ""
Test-Command helm | Out-Null
Write-Host ""
Test-Command git | Out-Null
Write-Host ""
Test-Command python | Out-Null
Write-Host ""

Write-Host "Environment check finished." -ForegroundColor Cyan
