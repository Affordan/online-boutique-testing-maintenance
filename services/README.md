# 新增微服务说明

本目录包含两个接入 Online-Boutique 的新增微服务（已替换原 ops-alert-service / user-log-service）。

## 1. coupon-service（优惠券 / 促销）

**接入对象：** `frontend`、`checkoutservice`

| 接口 | 调用方 | 说明 |
|------|--------|------|
| `GET /health` | 运维 | 健康检查 |
| `GET /coupons` | frontend | 列出可用促销 |
| `POST /coupons/validate` | frontend | 购物车页校验优惠码 |
| `POST /coupons/apply` | checkoutservice | 结账时应用优惠 |
| `GET /coupons/applied/{order_id}` | checkoutservice | 查询订单优惠记录 |
| `GET /metrics` | Prometheus | 指标 |

集群内地址：`http://coupon-service:8080`

## 2. inventory-service（库存）

**接入对象：** `productcatalogservice`、`checkoutservice`

| 接口 | 调用方 | 说明 |
|------|--------|------|
| `GET /health` | 运维 | 健康检查 |
| `GET /inventory` | productcatalogservice | 库存列表 |
| `GET /inventory/{product_id}` | productcatalogservice | 查询单品库存 |
| `POST /inventory/sync` | productcatalogservice | 同步商品库存 |
| `POST /inventory/reserve` | checkoutservice | 下单预留库存 |
| `POST /inventory/release` | checkoutservice | 取消订单释放库存 |
| `GET /metrics` | Prometheus | 指标 |

集群内地址：`http://inventory-service:8080`

## 3. 部署与接入

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\deploy_custom_services.ps1
```

`services/integration/k8s-env-integration.yaml` 会向以下 Deployment 注入环境变量：

- `frontend` → `COUPON_SERVICE_ADDR`、`INVENTORY_SERVICE_ADDR`
- `checkoutservice` → `COUPON_SERVICE_ADDR`、`INVENTORY_SERVICE_ADDR`
- `productcatalogservice` → `INVENTORY_SERVICE_ADDR`

## 4. 本地快速验证

```powershell
# coupon-service
cd services\coupon-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080

# 另开终端
curl http://localhost:8080/coupons
curl -X POST http://localhost:8080/coupons/validate -H "Content-Type: application/json" -d "{\"code\":\"SAVE10\",\"cart_total\":49.99}"
```

```powershell
# inventory-service
cd services\inventory-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8081

curl http://localhost:8081/inventory/OLJCESPC7Z
```
