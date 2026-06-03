param(
    [string]$Namespace = "online-boutique"
)

Write-Host "Watching Online-Boutique pods in namespace: $Namespace" -ForegroundColor Cyan
Write-Host "Press Ctrl + C to stop watching."
kubectl get pods -n $Namespace -w
