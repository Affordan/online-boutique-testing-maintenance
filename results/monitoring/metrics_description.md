# Monitoring Metrics Description

本文说明 `normal_metrics.csv` 与 `fault_metrics_raw.csv` 的字段、单位和 Prometheus 数据来源，供 F 进行异常检测建模时解释数据。

| 字段名 | 单位 | 来源 | 说明 |
|---|---|---|---|
| `timestamp` | datetime | 导出脚本采样时间 | CSV 采样时间，本地时区格式 |
| `experiment_id` | string | 导出参数 | 实验编号，例如 `EXP_001` |
| `service` | string | 应用指标 `service` label / `kube_pod_labels.label_app` | 服务名；请求、错误和延迟类指标由 `coupon-service` / `inventory-service` 显式暴露 `service` label |
| `pod` | string | Kubernetes pod label | Pod 名称 |
| `scenario` | string | 导出参数 | 场景，例如 `normal_traffic`、`fault_traffic` |
| `cpu_usage` | core/s | `rate(container_cpu_usage_seconds_total[5m])` | 5 分钟窗口 CPU 使用速率 |
| `memory_usage_mb` | MB | `container_memory_working_set_bytes` | 工作集内存，脚本转换为 MB |
| `restart_count` | count | `kube_pod_container_status_restarts_total` | 当前容器累计重启次数 |
| `request_rate` | req/s | `coupon_service_requests_total` / `inventory_service_requests_total` | 新增服务每秒请求数 |
| `error_rate` | ratio | 4xx+5xx 请求速率 / 总请求速率 | 新增服务错误率 |
| `avg_latency_ms` | ms | `*_request_duration_seconds_sum/count` | 新增服务平均响应时间 |
| `p95_latency_ms` | ms | `histogram_quantile(0.95, *_request_duration_seconds_bucket)` | 新增服务 P95 响应时间 |
| `throughput` | req/s | 同 `request_rate` | 当前阶段以请求速率作为吞吐量 |
| `http_2xx_rate` | req/s | `*_requests_total{status=~"2.."}` | 2xx 响应速率 |
| `http_4xx_rate` | req/s | `*_requests_total{status=~"4.."}` | 4xx 响应速率 |
| `http_5xx_rate` | req/s | `*_requests_total{status=~"5.."}` | 5xx 响应速率 |
| `network_receive_bytes` | bytes/s | `rate(container_network_receive_bytes_total[5m])` | Pod 网络接收速率 |
| `network_transmit_bytes` | bytes/s | `rate(container_network_transmit_bytes_total[5m])` | Pod 网络发送速率 |

注意：Online-Boutique 原系统默认主要提供 Kubernetes/容器层指标。请求速率、错误率和延迟字段主要来自 `coupon-service` 与 `inventory-service` 的 `/metrics`。ServiceMonitor 设置了 `honorLabels: true`，以保留业务指标自身暴露的 `service` label。
