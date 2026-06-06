#!/bin/bash
set -euo pipefail

MONITORING_NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
RELEASE_NAME="${RELEASE_NAME:-monitoring-stack}"

kubectl port-forward "svc/${RELEASE_NAME}-kube-prom-prometheus" 9090:9090 -n "${MONITORING_NAMESPACE}"
