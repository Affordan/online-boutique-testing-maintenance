param(
    [string]$Namespace = "online-boutique"
)

kubectl port-forward svc/inventory-service 18082:8080 -n $Namespace
