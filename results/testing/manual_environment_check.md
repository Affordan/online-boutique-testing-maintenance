# 环境与新增服务接口验证记录

## 1. 测试时间

2026-06-04

原始命令输出来自本地 PowerShell 验证记录，服务返回时间为 2026-06-04 08:03 至 08:09 UTC。

## 2. 测试环境

* Kubernetes Namespace：online-boutique
* Online-Boutique 前端地址：http://localhost:8080
* coupon-service 本地转发地址：http://localhost:18081
* inventory-service 本地转发地址：http://localhost:18082
* 当前 Git 分支：feature/Cololist-testing

## 3. Online-Boutique 主系统验证

执行 `.\scripts\wait_online_boutique.ps1` 后，Online-Boutique 主系统核心 Pod 均处于 Running 状态，READY 均为 1/1，RESTARTS 为 0。

已观察到正常运行的服务包括：

* adservice
* cartservice
* checkoutservice
* currencyservice
* emailservice
* frontend
* loadgenerator
* paymentservice
* productcatalogservice
* recommendationservice
* redis-cart
* shippingservice

结论：Online-Boutique 主系统已成功部署，具备后续功能测试与性能测试条件。

## 4. coupon-service 接口验证

### 4.1 健康检查

请求：

```powershell
curl http://localhost:18081/health
```

结果：

* HTTP 状态码：200 OK
* service：coupon-service
* integrated_with：frontend, checkoutservice

结论：coupon-service 健康检查通过。

### 4.2 优惠券列表查询

请求：

```powershell
curl http://localhost:18081/coupons
```

结果：

* HTTP 状态码：200 OK
* 返回 promotions 列表
* 当前可用优惠码包括 SAVE10、WELCOME5 等

结论：coupon-service 能正常返回优惠券规则。

### 4.3 优惠码校验

请求方式：

```powershell
$body = @{
  code = "SAVE10"
  cart_total = 49.99
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:18081/coupons/validate" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

结果：

* code：SAVE10
* valid：True
* discount：5.0
* final_total：44.99
* caller：frontend

结论：coupon-service 能正确校验 SAVE10 优惠码，并根据订单金额计算折扣与最终金额。

## 5. inventory-service 接口验证

### 5.1 健康检查

请求：

```powershell
curl http://localhost:18082/health
```

结果：

* HTTP 状态码：200 OK
* service：inventory-service
* integrated_with：productcatalogservice, checkoutservice

结论：inventory-service 健康检查通过。

### 5.2 库存列表查询

请求：

```powershell
curl http://localhost:18082/inventory
```

结果：

* HTTP 状态码：200 OK
* 返回 items 库存列表
* 包含 product_id、name、stock、reserved、available 等字段

结论：inventory-service 能正常返回商品库存列表。

### 5.3 单商品库存查询

请求：

```powershell
curl http://localhost:18082/inventory/OLJCESPC7Z
```

结果：

* HTTP 状态码：200 OK
* product_id：OLJCESPC7Z
* name：Vintage Typewriter
* stock：25
* reserved：0
* available：25
* caller：productcatalogservice

结论：inventory-service 能正常返回指定商品库存信息。

## 6. 当前阶段测试限制

当前 coupon-service 和 inventory-service 已完成接口级验证，但前端 UI 是否已经真正调用优惠券和库存接口，取决于前端返工完成情况。

因此，本阶段先完成新增服务的接口级验证和后续 JMeter 压测准备；Selenium 测试暂时优先覆盖 Online-Boutique 原有 UI 主流程，包括首页访问、商品详情页、加入购物车、查看购物车和结账流程。前端返工完成后，再补充优惠码输入、折扣展示、库存展示和库存不足等 UI 层 E2E 测试。
