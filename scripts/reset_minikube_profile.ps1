param(
    [string]$ProfileName = "online-boutique-lab"
)

$ErrorActionPreference = "Continue"

Write-Host "Deleting Minikube profile: $ProfileName" -ForegroundColor Yellow
minikube delete -p $ProfileName

Write-Host "Profile deleted. Run .\scripts\start_minikube.ps1 to create it again." -ForegroundColor Green
