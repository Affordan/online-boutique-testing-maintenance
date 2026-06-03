param(
    [string]$Namespace = "online-boutique",
    [int]$LocalPort = 8080
)

Write-Host "Forwarding frontend service to http://localhost:$LocalPort" -ForegroundColor Cyan
Write-Host "Press Ctrl + C to stop port forwarding."
kubectl port-forward svc/frontend "$($LocalPort):80" -n $Namespace
