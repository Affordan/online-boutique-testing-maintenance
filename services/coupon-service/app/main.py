import os
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

app = FastAPI(title="coupon-service", version="1.0.0", description="Coupon / promotion service for frontend and checkout")

CHECKOUT_SERVICE_ADDR = os.getenv("CHECKOUT_SERVICE_ADDR", "checkoutservice:5050")

PROMOTIONS: dict[str, dict[str, Any]] = {
    "SAVE10": {"code": "SAVE10", "type": "percent", "value": 10, "min_amount": 20.0, "description": "10% off orders over $20"},
    "WELCOME5": {"code": "WELCOME5", "type": "fixed", "value": 5.0, "min_amount": 0.0, "description": "$5 off first order"},
    "VIP15": {"code": "VIP15", "type": "percent", "value": 15, "min_amount": 50.0, "description": "15% off orders over $50"},
}

applied_coupons: dict[str, dict[str, Any]] = {}

REQUEST_COUNT = Counter("coupon_service_requests_total", "HTTP requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("coupon_service_request_duration_seconds", "HTTP latency")


class ValidateRequest(BaseModel):
    code: str = Field(..., examples=["SAVE10"])
    cart_total: float = Field(..., ge=0, examples=[49.99])
    user_id: str = Field(default="guest", examples=["test-user-001"])


class ApplyRequest(BaseModel):
    code: str
    order_id: str
    cart_total: float = Field(..., ge=0)
    user_id: str = "guest"


@app.middleware("http")
async def metrics_middleware(request, call_next):
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    return response


def calculate_discount(promo: dict[str, Any], cart_total: float) -> float:
    if cart_total < promo["min_amount"]:
        return 0.0
    if promo["type"] == "percent":
        return round(cart_total * promo["value"] / 100, 2)
    return min(promo["value"], cart_total)


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "coupon-service",
        "integrated_with": "frontend, checkoutservice",
    }


@app.get("/coupons")
async def list_coupons() -> dict[str, Any]:
    return {"promotions": list(PROMOTIONS.values())}


@app.post("/coupons/validate")
async def validate_coupon(body: ValidateRequest) -> dict[str, Any]:
    code = body.code.upper().strip()
    promo = PROMOTIONS.get(code)
    if not promo:
        raise HTTPException(status_code=404, detail="coupon not found")

    discount = calculate_discount(promo, body.cart_total)
    valid = discount > 0
    return {
        "code": code,
        "valid": valid,
        "discount": discount,
        "final_total": round(body.cart_total - discount, 2),
        "promotion": promo,
        "caller": "frontend",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/coupons/apply")
async def apply_coupon(body: ApplyRequest) -> dict[str, Any]:
    code = body.code.upper().strip()
    promo = PROMOTIONS.get(code)
    if not promo:
        raise HTTPException(status_code=404, detail="coupon not found")

    discount = calculate_discount(promo, body.cart_total)
    if discount <= 0:
        raise HTTPException(status_code=400, detail="coupon not applicable for this order amount")

    record = {
        "order_id": body.order_id,
        "code": code,
        "discount": discount,
        "final_total": round(body.cart_total - discount, 2),
        "user_id": body.user_id,
        "caller": "checkoutservice",
        "checkout_addr": CHECKOUT_SERVICE_ADDR,
        "applied_at": datetime.now(timezone.utc).isoformat(),
    }
    applied_coupons[body.order_id] = record
    return {"message": "coupon applied", "application": record}


@app.get("/coupons/applied/{order_id}")
async def get_applied(order_id: str) -> dict[str, Any]:
    record = applied_coupons.get(order_id)
    if not record:
        raise HTTPException(status_code=404, detail="no coupon applied for this order")
    return record


@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
