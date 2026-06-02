# Online-Boutique Monitoring PromQL

本文记录 Grafana 看板和 Prometheus 手动验证使用的核心查询语句。

## 基础资源指标

### Pod 运行状态

```promql
sum by (phase) (kube_pod_status_phase{namespace="online-boutique"})
```

### Running Pod 数量

```promql
sum(kube_pod_status_phase{namespace="online-boutique", phase="Running"})
```

### Pod 重启次数

```promql
sum by (pod) (increase(kube_pod_container_status_restarts_total{namespace="online-boutique"}[30m]))
```

### Pod CPU 使用率

```promql
sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="online-boutique", container!="", image!=""}[5m]))
```

### Pod 内存使用量

```promql
sum by (pod) (container_memory_working_set_bytes{namespace="online-boutique", container!="", image!=""})
```

### Pod 网络接收流量

```promql
sum by (pod) (rate(container_network_receive_bytes_total{namespace="online-boutique"}[5m]))
```

### Pod 网络发送流量

```promql
sum by (pod) (rate(container_network_transmit_bytes_total{namespace="online-boutique"}[5m]))
```

## 新增微服务应用指标

以下查询依赖新增微服务暴露 Prometheus 格式的 `/metrics`，并在 Service 上添加 `monitoring: enabled` label。

### 请求量

```promql
sum by (service) (rate(http_requests_total{namespace="online-boutique"}[5m]))
```

### 错误率

```promql
sum by (service) (rate(http_requests_total{namespace="online-boutique", status=~"5.."}[5m]))
/
sum by (service) (rate(http_requests_total{namespace="online-boutique"}[5m]))
```

### P95 请求延迟

```promql
histogram_quantile(
  0.95,
  sum by (le, service) (
    rate(http_request_duration_seconds_bucket{namespace="online-boutique"}[5m])
  )
)
```

### 服务健康状态

```promql
up{namespace="online-boutique", job=~".*ops-alert-service.*|.*user-log-service.*"}
```
