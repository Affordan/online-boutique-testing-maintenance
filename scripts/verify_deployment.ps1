param(
    [string]$Namespace = "online-boutique"
)

Write-Host "Current context:" -ForegroundColor Cyan
kubectl config current-context

Write-Host ""
Write-Host "Nodes:" -ForegroundColor Cyan
kubectl get nodes -o wide

Write-Host ""
Write-Host "Pods in $Namespace:" -ForegroundColor Cyan
kubectl get pods -n $Namespace

Write-Host ""
Write-Host "Services in $Namespace:" -ForegroundColor Cyan
kubectl get svc -n $Namespace
