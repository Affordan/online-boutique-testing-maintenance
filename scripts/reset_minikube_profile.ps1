param(
    [string]$ProfileName = "online-boutique-lab"
)

Write-Host "Deleting Minikube profile: $ProfileName" -ForegroundColor Yellow
minikube delete -p $ProfileName
