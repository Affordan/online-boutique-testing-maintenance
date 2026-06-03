param(
    [string]$Namespace = "online-boutique"
)

Write-Host "Current kubectl context:" -ForegroundColor Cyan
kubectl config current-context

Write-Host ""
Write-Host "Nodes:" -ForegroundColor Cyan
kubectl get nodes

Write-Host ""
Write-Host "Pods:" -ForegroundColor Cyan
kubectl get pods -n $Namespace

Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
kubectl get svc -n $Namespace

Write-Host ""
Write-Host "If frontend is Running, use:" -ForegroundColor Green
Write-Host ".\scripts\port_forward_frontend.ps1"
