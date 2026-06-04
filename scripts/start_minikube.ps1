param(
    [string]$ProfileName = "online-boutique-lab",
    [int]$Cpus = 4,
    [int]$Memory = 6144
)

$ErrorActionPreference = "Stop"

Write-Host "Starting Minikube profile: $ProfileName" -ForegroundColor Cyan
Write-Host "Driver: docker, CPUs: $Cpus, Memory: $Memory MB" -ForegroundColor Cyan

minikube start -p $ProfileName --driver=docker --cpus=$Cpus --memory=$Memory
if ($LASTEXITCODE -ne 0) { throw "minikube start failed" }

minikube update-context -p $ProfileName
kubectl config use-context $ProfileName

Write-Host ""
Write-Host "Current context:" -ForegroundColor Cyan
kubectl config current-context

Write-Host ""
Write-Host "Nodes:" -ForegroundColor Cyan
kubectl get nodes
