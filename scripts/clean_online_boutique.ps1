param(
    [string]$Namespace = "online-boutique",
    [switch]$Wait
)

Write-Host "Deleting namespace: $Namespace" -ForegroundColor Yellow

if ($Wait) {
    kubectl delete namespace $Namespace --ignore-not-found=true
} else {
    kubectl delete namespace $Namespace --ignore-not-found=true --wait=false
}

Write-Host "Delete command submitted." -ForegroundColor Green
