# 性能测试说明

## 测试对象

```text
frontend: http://localhost:8080
coupon-service: http://localhost:18081
inventory-service: http://localhost:18082
```

## 测试前置条件

需要分别保持以下端口转发窗口运行：

```powershell
.\scripts\port_forward_frontend.ps1
kubectl port-forward svc/coupon-service 18081:8080 -n online-boutique
kubectl port-forward svc/inventory-service 18082:8080 -n online-boutique
```

## 测试场景

| 场景 | 并发数 | 持续时间 | 说明 |
| --- | ---: | ---: | --- |
| jmeter_10_users | 10 | 600 s | 低并发正常流量 |
| jmeter_30_users | 30 | 600 s | 中并发正常流量，可配合 Pod Kill |
| jmeter_50_users | 50 | 900 s | 高并发流量，可配合 CPU 或网络延迟故障 |
| jmeter_100_users | 100 | 900 s | 极限并发流量，可配合故障期间压测 |

## 覆盖接口

```text
GET  /
GET  /product/OLJCESPC7Z
GET  /cart
GET  /health                  coupon-service
GET  /coupons                 coupon-service
POST /coupons/validate        coupon-service
GET  /health                  inventory-service
GET  /inventory               inventory-service
GET  /inventory/OLJCESPC7Z    inventory-service
```

## 输出文件

```text
results/testing/jmeter_results.csv
results/testing/jmeter_summary.csv
figures/testing/jmeter_summary_10_30_50_100.png
figures/testing/jmeter_summary_100.png
figures/testing/jmeter_aggregate_report.png
figures/testing/jmeter_response_time.png
figures/testing/jmeter_throughput.png
```
