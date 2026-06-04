param(
    [string]$Namespace = "online-boutique"
)

Write-Host "Deleting namespace: $Namespace" -ForegroundColor Yellow
kubectl delete namespace $Namespace --ignore-not-found=true
