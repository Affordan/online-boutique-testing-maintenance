from collections import Counter
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter as PromCounter, Histogram, generate_latest
from pydantic import BaseModel, Field

app = FastAPI(title="user-log-service", version="1.0.0")

logs: list[dict[str, Any]] = []

REQUEST_COUNT = PromCounter("user_log_requests_total", "Total HTTP requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("user_log_request_duration_seconds", "HTTP request latency")


class LogEntry(BaseModel):
    user_id: str = Field(..., examples=["test-user-001"])
    action: str = Field(..., examples=["add_to_cart"])
    service: str = Field(..., examples=["frontend"])
    response_time: float = Field(..., ge=0, examples=[0.42])
    status: str = Field(..., examples=["success"])
    timestamp: str | None = Field(default=None, examples=["2026-06-01 10:00:00"])


@app.middleware("http")
async def metrics_middleware(request, call_next):
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "user-log-service"}


@app.post("/log")
async def create_log(entry: LogEntry) -> dict[str, Any]:
    record = entry.model_dump()
    if not record.get("timestamp"):
        record["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    logs.append(record)
    return {"message": "log recorded", "log": record}


@app.get("/logs")
async def list_logs(
    user_id: str | None = Query(default=None),
    action: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
) -> dict[str, Any]:
    filtered = logs
    if user_id:
        filtered = [item for item in filtered if item["user_id"] == user_id]
    if action:
        filtered = [item for item in filtered if item["action"] == action]
    filtered = filtered[-limit:]
    return {"count": len(filtered), "logs": filtered}


@app.get("/stats")
async def stats() -> dict[str, Any]:
    action_counter = Counter(item["action"] for item in logs)
    status_counter = Counter(item["status"] for item in logs)
    service_counter = Counter(item["service"] for item in logs)
    response_times = [item["response_time"] for item in logs]

    avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
    return {
        "total_logs": len(logs),
        "actions": dict(action_counter),
        "statuses": dict(status_counter),
        "services": dict(service_counter),
        "avg_response_time": round(avg_response_time, 3),
    }


@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
