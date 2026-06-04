#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen


CSV_FIELDS = [
    "timestamp",
    "experiment_id",
    "service",
    "pod",
    "scenario",
    "cpu_usage",
    "memory_usage_mb",
    "restart_count",
    "request_rate",
    "error_rate",
    "avg_latency_ms",
    "p95_latency_ms",
    "throughput",
    "http_2xx_rate",
    "http_4xx_rate",
    "http_5xx_rate",
    "network_receive_bytes",
    "network_transmit_bytes",
]

APP_SERVICES = ("coupon-service", "inventory-service")


def prom_query(base_url: str, expr: str) -> list[dict]:
    url = base_url.rstrip("/") + "/api/v1/query?" + urlencode({"query": expr})
    with urlopen(url, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("status") != "success":
        raise RuntimeError(f"Prometheus query failed: {expr}")
    return payload.get("data", {}).get("result", [])


def value_by_label(base_url: str, expr: str, label: str) -> dict[str, float]:
    values: dict[str, float] = {}
    for item in prom_query(base_url, expr):
        key = item.get("metric", {}).get(label)
        if not key:
            continue
        values[key] = float(item.get("value", [0, "0"])[1])
    return values


def pod_service_map(base_url: str) -> dict[str, str]:
    expr = 'kube_pod_labels{namespace="online-boutique", label_app!=""}'
    mapping: dict[str, str] = {}
    for item in prom_query(base_url, expr):
        metric = item.get("metric", {})
        pod = metric.get("pod")
        service = metric.get("label_app")
        if pod and service:
            mapping[pod] = service
    return mapping


def service_values(base_url: str, expr_template: str) -> dict[str, float]:
    return value_by_label(base_url, expr_template, "service")


def build_rows(base_url: str, experiment_id: str, scenario: str) -> list[dict]:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pod_to_service = pod_service_map(base_url)

    cpu = value_by_label(
        base_url,
        'sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="online-boutique"}[5m]))',
        "pod",
    )
    memory = value_by_label(
        base_url,
        'sum by (pod) (container_memory_working_set_bytes{namespace="online-boutique"}) / 1024 / 1024',
        "pod",
    )
    restarts = value_by_label(
        base_url,
        'sum by (pod) (kube_pod_container_status_restarts_total{namespace="online-boutique"})',
        "pod",
    )
    network_receive = value_by_label(
        base_url,
        'sum by (pod) (rate(container_network_receive_bytes_total{namespace="online-boutique"}[5m]))',
        "pod",
    )
    network_transmit = value_by_label(
        base_url,
        'sum by (pod) (rate(container_network_transmit_bytes_total{namespace="online-boutique"}[5m]))',
        "pod",
    )

    request_rate = service_values(
        base_url,
        'sum by (service) (rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique"}[5m]))',
    )
    http_2xx = service_values(
        base_url,
        'sum by (service) (rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique", status=~"2.."}[5m]))',
    )
    http_4xx = service_values(
        base_url,
        'sum by (service) (rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique", status=~"4.."}[5m]))',
    )
    http_5xx = service_values(
        base_url,
        'sum by (service) (rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique", status=~"5.."}[5m]))',
    )
    avg_latency = service_values(
        base_url,
        '1000 * sum by (service) (rate({__name__=~"coupon_service_request_duration_seconds_sum|inventory_service_request_duration_seconds_sum", namespace="online-boutique"}[5m])) / sum by (service) (rate({__name__=~"coupon_service_request_duration_seconds_count|inventory_service_request_duration_seconds_count", namespace="online-boutique"}[5m]))',
    )
    p95_latency = service_values(
        base_url,
        '1000 * histogram_quantile(0.95, sum by (le, service) (rate({__name__=~"coupon_service_request_duration_seconds_bucket|inventory_service_request_duration_seconds_bucket", namespace="online-boutique"}[5m])))',
    )

    rows: list[dict] = []
    for pod, service in sorted(pod_to_service.items()):
        total_rate = request_rate.get(service, 0.0)
        errors = http_4xx.get(service, 0.0) + http_5xx.get(service, 0.0)
        error_rate = errors / total_rate if total_rate > 0 else 0.0
        row = {
            "timestamp": timestamp,
            "experiment_id": experiment_id,
            "service": service,
            "pod": pod,
            "scenario": scenario,
            "cpu_usage": cpu.get(pod, 0.0),
            "memory_usage_mb": memory.get(pod, 0.0),
            "restart_count": int(restarts.get(pod, 0.0)),
            "request_rate": total_rate,
            "error_rate": error_rate,
            "avg_latency_ms": avg_latency.get(service, 0.0),
            "p95_latency_ms": p95_latency.get(service, 0.0),
            "throughput": total_rate,
            "http_2xx_rate": http_2xx.get(service, 0.0),
            "http_4xx_rate": http_4xx.get(service, 0.0),
            "http_5xx_rate": http_5xx.get(service, 0.0),
            "network_receive_bytes": network_receive.get(pod, 0.0),
            "network_transmit_bytes": network_transmit.get(pod, 0.0),
        }
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Online-Boutique monitoring metrics from Prometheus.")
    parser.add_argument("--prometheus-url", default="http://localhost:9090")
    parser.add_argument("--experiment-id", default="EXP_001")
    parser.add_argument("--scenario", default="normal_traffic")
    parser.add_argument("--output", default="data/raw/normal_metrics.csv")
    args = parser.parse_args()

    rows = build_rows(args.prometheus_url, args.experiment_id, args.scenario)
    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
