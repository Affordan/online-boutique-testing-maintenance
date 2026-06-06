#!/bin/bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-online-boutique}"
MINIKUBE_PROFILE="${MINIKUBE_PROFILE:-minikube}"

docker build --pull=false -t coupon-service:latest services/coupon-service
docker build --pull=false -t inventory-service:latest services/inventory-service

minikube -p "${MINIKUBE_PROFILE}" image load coupon-service:latest
minikube -p "${MINIKUBE_PROFILE}" image load inventory-service:latest

kubectl apply -f services/coupon-service/k8s -n "${NAMESPACE}"
kubectl apply -f services/inventory-service/k8s -n "${NAMESPACE}"

kubectl set env deployment/frontend \
  COUPON_SERVICE_ADDR=http://coupon-service:8080 \
  INVENTORY_SERVICE_ADDR=http://inventory-service:8080 \
  -n "${NAMESPACE}"

kubectl set env deployment/checkoutservice \
  COUPON_SERVICE_ADDR=http://coupon-service:8080 \
  INVENTORY_SERVICE_ADDR=http://inventory-service:8080 \
  -n "${NAMESPACE}"

kubectl set env deployment/productcatalogservice \
  INVENTORY_SERVICE_ADDR=http://inventory-service:8080 \
  -n "${NAMESPACE}"

kubectl rollout status deployment/coupon-service -n "${NAMESPACE}" --timeout=120s
kubectl rollout status deployment/inventory-service -n "${NAMESPACE}" --timeout=120s
kubectl rollout status deployment/frontend -n "${NAMESPACE}" --timeout=180s
kubectl rollout status deployment/checkoutservice -n "${NAMESPACE}" --timeout=180s
kubectl rollout status deployment/productcatalogservice -n "${NAMESPACE}" --timeout=180s

kubectl get pods -n "${NAMESPACE}"
kubectl get svc -n "${NAMESPACE}"
