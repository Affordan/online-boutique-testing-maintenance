param(
    [string]$ProfileName = "online-boutique-lab",
    [string]$Namespace = "online-boutique",
    [int]$Cpus = 4,
    [int]$Memory = 6144
)

$ErrorActionPreference = "Stop"

& "$PSScriptRoot\download_online_boutique_manifest.ps1"
& "$PSScriptRoot\start_minikube.ps1" -ProfileName $ProfileName -Cpus $Cpus -Memory $Memory
& "$PSScriptRoot\deploy_online_boutique.ps1" -Namespace $Namespace

Write-Host "Fresh deployment submitted." -ForegroundColor Green
Write-Host "Next: .\scripts\wait_online_boutique.ps1" -ForegroundColor Cyan
