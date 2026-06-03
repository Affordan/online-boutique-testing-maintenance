param(
    [string]$ProfileName = "online-boutique-lab",
    [int]$Cpus = 4,
    [int]$Memory = 6144,
    [switch]$PreloadImages
)

$ErrorActionPreference = "Stop"

Write-Host "Fresh deployment for Online-Boutique" -ForegroundColor Cyan
Write-Host "Profile: $ProfileName"
Write-Host "CPUs: $Cpus, Memory: $Memory MB"
Write-Host ""

& "$PSScriptRoot\download_online_boutique_manifest.ps1"
& "$PSScriptRoot\start_minikube.ps1" -ProfileName $ProfileName -Cpus $Cpus -Memory $Memory

if ($PreloadImages) {
    & "$PSScriptRoot\preload_images_to_minikube.ps1" -ProfileName $ProfileName
}

& "$PSScriptRoot\deploy_online_boutique.ps1"

Write-Host ""
Write-Host "Fresh deployment submitted." -ForegroundColor Green
Write-Host "Next command:" -ForegroundColor Cyan
Write-Host ".\scripts\wait_online_boutique.ps1"
Write-Host ""
Write-Host "If pods show ImagePullBackOff, run:" -ForegroundColor Yellow
Write-Host ".\scripts\preload_images_to_minikube.ps1 -RestartPods"
