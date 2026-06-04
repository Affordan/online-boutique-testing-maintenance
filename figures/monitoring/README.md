# Monitoring Screenshot Checklist

请在本地部署完成后保存以下截图，文件名需要与课程 C 任务要求完全一致：

| 文件名 | 截图内容 | 截取时机 |
|---|---|---|
| `prometheus_targets.png` | Prometheus Targets 页面，包含 Kubernetes targets 和 `coupon-service` / `inventory-service` | 正常流量阶段 |
| `grafana_overview.png` | Online Boutique 总览 Dashboard | 正常流量阶段 |
| `grafana_coupon_inventory.png` | Coupon Inventory Monitoring Overview 专项 Dashboard | 正常流量或压测阶段 |
| `grafana_fault_compare.png` | 故障注入前后指标变化曲线 | D 注入故障、E 提供流量后 |

截图建议保存到当前目录：

```text
figures/monitoring/
```
