param(
    [string]$Namespace = "online-boutique"
)

Write-Host "Deleting coupon-service and inventory-service..." -ForegroundColor Yellow
kubectl delete -f .\services\coupon-service\k8s -n $Namespace --ignore-not-found=true
kubectl delete -f .\services\inventory-service\k8s -n $Namespace --ignore-not-found=true

Write-Host "Removing injected env vars from original deployments..." -ForegroundColor Yellow
kubectl set env deployment/frontend COUPON_SERVICE_ADDR- INVENTORY_SERVICE_ADDR- -n $Namespace
kubectl set env deployment/checkoutservice COUPON_SERVICE_ADDR- INVENTORY_SERVICE_ADDR- -n $Namespace
kubectl set env deployment/productcatalogservice INVENTORY_SERVICE_ADDR- -n $Namespace
