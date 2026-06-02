#!/bin/bash
set -euo pipefail

kubectl create namespace online-boutique --dry-run=client -o yaml | kubectl apply -f -

test -f deploy/online-boutique/kubernetes-manifests.yaml
kubectl apply -f deploy/online-boutique/kubernetes-manifests.yaml -n online-boutique

kubectl get pods -n online-boutique
kubectl get svc -n online-boutique
