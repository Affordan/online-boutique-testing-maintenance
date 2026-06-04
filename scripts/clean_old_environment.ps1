param(
    [string]$ProjectProfile = "online-boutique-lab",
    [string]$OldProfile = "minikube",
    [string]$Namespace = "online-boutique",
    [switch]$DeleteProjectProfile,
    [switch]$StopOldProfile,
    [switch]$DeleteOldProfile
)

Write-Host "Minikube profiles before cleanup:" -ForegroundColor Cyan
minikube profile list

Write-Host ""
Write-Host "Cleaning Online-Boutique namespace in current context if it exists..." -ForegroundColor Yellow
kubectl delete namespace $Namespace --ignore-not-found=true

if ($DeleteProjectProfile) {
    Write-Host "Deleting project profile: $ProjectProfile" -ForegroundColor Yellow
    minikube delete -p $ProjectProfile
}

if ($StopOldProfile) {
    Write-Host "Stopping old default profile: $OldProfile" -ForegroundColor Yellow
    minikube stop -p $OldProfile
}

if ($DeleteOldProfile) {
    Write-Host "Deleting old default profile: $OldProfile" -ForegroundColor Red
    minikube delete -p $OldProfile
}

Write-Host ""
Write-Host "Minikube profiles after cleanup:" -ForegroundColor Cyan
minikube profile list
