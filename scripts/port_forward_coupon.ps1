param(
    [string]$Namespace = "online-boutique"
)

kubectl port-forward svc/coupon-service 18081:8080 -n $Namespace
