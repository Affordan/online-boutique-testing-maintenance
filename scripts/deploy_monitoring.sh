#!/bin/bash
set -euo pipefail

MONITORING_NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
RELEASE_NAME="${RELEASE_NAME:-monitoring-stack}"
CHART_NAME="prometheus-community/kube-prometheus-stack"

kubectl create namespace "${MONITORING_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install "${RELEASE_NAME}" "${CHART_NAME}" \
  --namespace "${MONITORING_NAMESPACE}" \
  --set grafana.sidecar.dashboards.enabled=true \
  --set grafana.sidecar.dashboards.searchNamespace="${MONITORING_NAMESPACE}" \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false

kubectl create configmap online-boutique-overview-dashboard \
  --from-file=online-boutique-overview.json=monitoring/grafana/dashboards/online-boutique-overview.json \
  --namespace "${MONITORING_NAMESPACE}" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl label configmap online-boutique-overview-dashboard \
  grafana_dashboard=1 \
  --namespace "${MONITORING_NAMESPACE}" \
  --overwrite

kubectl apply -f monitoring/prometheus/servicemonitor-custom-services.yaml

kubectl get pods -n "${MONITORING_NAMESPACE}"

cat <<INFO

Monitoring stack deployed.

Grafana:
  bash scripts/port_forward_grafana.sh
  http://localhost:3000

Prometheus:
  bash scripts/port_forward_prometheus.sh
  http://localhost:9090

Grafana admin password:
  kubectl get secret -n ${MONITORING_NAMESPACE} ${RELEASE_NAME}-grafana -o jsonpath="{.data.admin-password}" | base64 --decode

INFO
