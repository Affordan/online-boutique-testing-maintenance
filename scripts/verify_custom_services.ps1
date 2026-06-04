param(
    [string]$Namespace = "online-boutique"
)

Write-Host "==> Custom service pods"
kubectl get pods -n $Namespace | findstr "coupon inventory"

Write-Host "==> Custom service services"
kubectl get svc -n $Namespace | findstr "coupon inventory"

Write-Host "==> frontend env"
kubectl describe deployment frontend -n $Namespace | findstr "COUPON INVENTORY"

Write-Host "==> checkoutservice env"
kubectl describe deployment checkoutservice -n $Namespace | findstr "COUPON INVENTORY"

Write-Host "==> productcatalogservice env"
kubectl describe deployment productcatalogservice -n $Namespace | findstr "INVENTORY"

Write-Host "==> Test commands"
Write-Host "kubectl port-forward svc/coupon-service 18081:8080 -n $Namespace"
Write-Host "kubectl port-forward svc/inventory-service 18082:8080 -n $Namespace"
Write-Host "Invoke-RestMethod http://localhost:18081/health"
Write-Host "Invoke-RestMethod http://localhost:18081/coupons"
Write-Host "Invoke-RestMethod http://localhost:18082/health"
Write-Host "Invoke-RestMethod http://localhost:18082/inventory/OLJCESPC7Z"
