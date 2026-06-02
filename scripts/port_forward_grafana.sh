#!/bin/bash
set -euo pipefail

MONITORING_NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
RELEASE_NAME="${RELEASE_NAME:-monitoring-stack}"

kubectl port-forward "svc/${RELEASE_NAME}-grafana" 3000:80 -n "${MONITORING_NAMESPACE}"
