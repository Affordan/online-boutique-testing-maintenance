import os
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090")
LATENCY_THRESHOLD = float(os.getenv("LATENCY_THRESHOLD", "1.0"))
ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", "0.05"))
CPU_THRESHOLD = float(os.getenv("CPU_THRESHOLD", "0.8"))

MONITORED_SERVICES = [
    "frontend",
    "cartservice",
    "checkoutservice",
    "productcatalogservice",
    "recommendationservice",
]

app = FastAPI(title="ops-alert-service", version="1.0.0")

REQUEST_COUNT = Counter("ops_alert_requests_total", "Total HTTP requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("ops_alert_request_duration_seconds", "HTTP request latency")


@app.middleware("http")
async def metrics_middleware(request, call_next):
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    return response


async def query_prometheus(query: str) -> float | None:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": query},
            )
            response.raise_for_status()
            payload = response.json()
            results = payload.get("data", {}).get("result", [])
            if not results:
                return None
            return float(results[0]["value"][1])
    except Exception:
        return None


async def build_service_summary(service: str) -> dict[str, Any]:
    latency = await query_prometheus(
        f'histogram_quantile(0.95, sum(rate(http_server_request_duration_seconds_bucket{{service="{service}"}}[5m])) by (le))'
    )
    error_rate = await query_prometheus(
        f'sum(rate(http_server_requests_total{{service="{service}",status=~"5.."}}[5m])) / '
        f'sum(rate(http_server_requests_total{{service="{service}"}}[5m]))'
    )
    cpu_usage = await query_prometheus(
        f'sum(rate(container_cpu_usage_seconds_total{{pod=~"{service}-.*",namespace="online-boutique"}}[5m]))'
    )

    return {
        "service": service,
        "latency_p95": latency,
        "error_rate": error_rate,
        "cpu_usage": cpu_usage,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def evaluate_alert(summary: dict[str, Any]) -> dict[str, Any] | None:
    service = summary["service"]
    latency = summary.get("latency_p95")
    error_rate = summary.get("error_rate")
    cpu_usage = summary.get("cpu_usage")

    if latency is not None and latency > LATENCY_THRESHOLD:
        return {
            "service": service,
            "status": "anomaly",
            "reason": "request latency exceeds threshold",
            "latency": round(latency, 3),
            "threshold": LATENCY_THRESHOLD,
        }
    if error_rate is not None and error_rate > ERROR_RATE_THRESHOLD:
        return {
            "service": service,
            "status": "anomaly",
            "reason": "error rate exceeds threshold",
            "error_rate": round(error_rate, 4),
            "threshold": ERROR_RATE_THRESHOLD,
        }
    if cpu_usage is not None and cpu_usage > CPU_THRESHOLD:
        return {
            "service": service,
            "status": "anomaly",
            "reason": "cpu usage exceeds threshold",
            "cpu_usage": round(cpu_usage, 3),
            "threshold": CPU_THRESHOLD,
        }
    return None


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ops-alert-service"}


@app.get("/metrics-summary")
async def metrics_summary() -> dict[str, Any]:
    summaries = [await build_service_summary(service) for service in MONITORED_SERVICES]
    return {"services": summaries, "generated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/alerts")
async def alerts() -> dict[str, Any]:
    summaries = [await build_service_summary(service) for service in MONITORED_SERVICES]
    active_alerts = [alert for summary in summaries if (alert := evaluate_alert(summary))]
    return {
        "alert_count": len(active_alerts),
        "alerts": active_alerts,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/check")
async def check() -> dict[str, Any]:
    summaries = [await build_service_summary(service) for service in MONITORED_SERVICES]
    active_alerts = [alert for summary in summaries if (alert := evaluate_alert(summary))]
    return {
        "status": "anomaly" if active_alerts else "normal",
        "alert_count": len(active_alerts),
        "alerts": active_alerts,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
