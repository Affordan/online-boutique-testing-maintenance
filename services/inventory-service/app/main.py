import os
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

app = FastAPI(title="inventory-service", version="1.0.0", description="Inventory service for productcatalog and checkout")

PRODUCT_CATALOG_ADDR = os.getenv("PRODUCT_CATALOG_SERVICE_ADDR", "productcatalogservice:3550")
CHECKOUT_SERVICE_ADDR = os.getenv("CHECKOUT_SERVICE_ADDR", "checkoutservice:5050")

DEFAULT_STOCK = int(os.getenv("DEFAULT_STOCK", "100"))

inventory: dict[str, dict[str, Any]] = {
    "OLJCESPC7Z": {"product_id": "OLJCESPC7Z", "name": "Vintage Typewriter", "stock": 25, "reserved": 0},
    "66VCHSJNUP": {"product_id": "66VCHSJNUP", "name": "Vintage Record Player", "stock": 40, "reserved": 0},
    "1YMWWN1N4O": {"product_id": "1YMWWN1N4O", "name": "Home Barista Kit", "stock": 60, "reserved": 0},
    "L9ECAV7KIM": {"product_id": "L9ECAV7KIM", "name": "Terrarium", "stock": 80, "reserved": 0},
    "2ZYFJ3GM2N": {"product_id": "2ZYFJ3GM2N", "name": "Film Camera", "stock": 35, "reserved": 0},
}

reservations: dict[str, dict[str, Any]] = {}

REQUEST_COUNT = Counter("inventory_service_requests_total", "HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("inventory_service_request_duration_seconds", "HTTP latency", ["method", "endpoint", "status"])


class ReserveRequest(BaseModel):
    order_id: str
    product_id: str
    quantity: int = Field(..., ge=1)


class ReleaseRequest(BaseModel):
    order_id: str


class SyncRequest(BaseModel):
    product_id: str
    name: str = "Unknown Product"
    stock: int = Field(default=DEFAULT_STOCK, ge=0)


@app.middleware("http")
async def metrics_middleware(request, call_next):
    started_at = time.perf_counter()
    status = "500"
    try:
        response = await call_next(request)
        status = str(response.status_code)
    finally:
        elapsed = time.perf_counter() - started_at
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path, status=status).observe(elapsed)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=status).inc()
    return response


def available_stock(item: dict[str, Any]) -> int:
    return item["stock"] - item["reserved"]


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "inventory-service",
        "integrated_with": "productcatalogservice, checkoutservice",
    }


@app.get("/inventory")
async def list_inventory() -> dict[str, Any]:
    return {
        "items": [
            {
                **item,
                "available": available_stock(item),
                "catalog_addr": PRODUCT_CATALOG_ADDR,
            }
            for item in inventory.values()
        ]
    }


@app.get("/inventory/{product_id}")
async def get_inventory(product_id: str) -> dict[str, Any]:
    item = inventory.get(product_id)
    if not item:
        raise HTTPException(status_code=404, detail="product not found in inventory")
    return {
        **item,
        "available": available_stock(item),
        "caller": "productcatalogservice",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/inventory/sync")
async def sync_inventory(body: SyncRequest) -> dict[str, Any]:
    item = inventory.get(body.product_id, {
        "product_id": body.product_id,
        "name": body.name,
        "stock": body.stock,
        "reserved": 0,
    })
    item["name"] = body.name
    item["stock"] = body.stock
    inventory[body.product_id] = item
    return {"message": "inventory synced", "item": item, "caller": "productcatalogservice"}


@app.post("/inventory/reserve")
async def reserve_inventory(body: ReserveRequest) -> dict[str, Any]:
    item = inventory.get(body.product_id)
    if not item:
        raise HTTPException(status_code=404, detail="product not found in inventory")

    if available_stock(item) < body.quantity:
        raise HTTPException(status_code=409, detail="insufficient stock")

    item["reserved"] += body.quantity
    record = {
        "order_id": body.order_id,
        "product_id": body.product_id,
        "quantity": body.quantity,
        "caller": "checkoutservice",
        "checkout_addr": CHECKOUT_SERVICE_ADDR,
        "reserved_at": datetime.now(timezone.utc).isoformat(),
    }
    reservations[body.order_id] = record
    return {"message": "stock reserved", "reservation": record, "available": available_stock(item)}


@app.post("/inventory/release")
async def release_inventory(body: ReleaseRequest) -> dict[str, Any]:
    record = reservations.pop(body.order_id, None)
    if not record:
        raise HTTPException(status_code=404, detail="reservation not found")

    item = inventory.get(record["product_id"])
    if item:
        item["reserved"] = max(0, item["reserved"] - record["quantity"])

    return {"message": "reservation released", "reservation": record}


@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
