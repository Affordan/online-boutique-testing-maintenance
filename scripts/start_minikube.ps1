param(
    [string]$ProfileName = "online-boutique-lab",
    [string]$Driver = "docker",
    [int]$Cpus = 4,
    [int]$Memory = 6144
)

$ErrorActionPreference = "Stop"

Write-Host "Starting Minikube profile: $ProfileName" -ForegroundColor Cyan
Write-Host "Driver: $Driver, CPUs: $Cpus, Memory: $Memory MB"

minikube start -p $ProfileName --driver=$Driver --cpus=$Cpus --memory=$Memory

kubectl config use-context $ProfileName

Write-Host ""
Write-Host "Current kubectl context:" -ForegroundColor Cyan
kubectl config current-context

Write-Host ""
Write-Host "Kubernetes nodes:" -ForegroundColor Cyan
kubectl get nodes

Write-Host ""
Write-Host "All pods:" -ForegroundColor Cyan
kubectl get pods -A
