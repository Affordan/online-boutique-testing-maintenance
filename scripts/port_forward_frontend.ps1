param(
    [string]$Namespace = "online-boutique",
    [int]$LocalPort = 8080
)

Write-Host "Forwarding frontend to http://localhost:$LocalPort" -ForegroundColor Cyan
Write-Host "Press Ctrl + C to stop." -ForegroundColor Yellow
kubectl port-forward svc/frontend ${LocalPort}:80 -n $Namespace
