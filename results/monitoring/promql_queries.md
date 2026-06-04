# Online-Boutique Monitoring PromQL

本文记录 C 监控任务使用的 PromQL，覆盖 Online-Boutique 原系统、`coupon-service` 和 `inventory-service`。

## 资源与 Pod 状态

### Pod 运行状态

```promql
sum by (phase) (kube_pod_status_phase{namespace="online-boutique"})
```

### Pod 重启次数

```promql
sum by (pod) (increase(kube_pod_container_status_restarts_total{namespace="online-boutique"}[30m]))
```

### Pod CPU 使用率

```promql
sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="online-boutique"}[5m]))
```

### Pod 内存使用量

```promql
sum by (pod) (container_memory_working_set_bytes{namespace="online-boutique"})
```

### Pod 网络接收流量

```promql
sum by (pod) (rate(container_network_receive_bytes_total{namespace="online-boutique"}[5m]))
```

### Pod 网络发送流量

```promql
sum by (pod) (rate(container_network_transmit_bytes_total{namespace="online-boutique"}[5m]))
```

## coupon-service / inventory-service 应用指标

### Prometheus 抓取状态

```promql
up{namespace="online-boutique", service=~"coupon-service|inventory-service"}
```

### 请求速率

```promql
sum by (service) (
  rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique"}[5m])
)
```

### 2xx 响应速率

```promql
sum by (service) (
  rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique", status=~"2.."}[5m])
)
```

### 4xx 响应速率

```promql
sum by (service) (
  rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique", status=~"4.."}[5m])
)
```

### 5xx 响应速率

```promql
sum by (service) (
  rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique", status=~"5.."}[5m])
)
```

### 错误率

```promql
sum by (service) (
  rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique", status=~"4..|5.."}[5m])
)
/
sum by (service) (
  rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique"}[5m])
)
```

### 平均延迟

```promql
sum by (service) (
  rate({__name__=~"coupon_service_request_duration_seconds_sum|inventory_service_request_duration_seconds_sum", namespace="online-boutique"}[5m])
)
/
sum by (service) (
  rate({__name__=~"coupon_service_request_duration_seconds_count|inventory_service_request_duration_seconds_count", namespace="online-boutique"}[5m])
)
```

### P95 延迟

```promql
histogram_quantile(
  0.95,
  sum by (le, service) (
    rate({__name__=~"coupon_service_request_duration_seconds_bucket|inventory_service_request_duration_seconds_bucket", namespace="online-boutique"}[5m])
  )
)
```
