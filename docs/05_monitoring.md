# Prometheus + Grafana 监控部署记录

本文记录 Online-Boutique 微服务系统的监控组件部署、指标接入、PromQL 查询和 Grafana 看板验证方式。

## 1. 目标

监控实验需要完成以下内容：

1. 部署 Prometheus 和 Grafana。
2. 接入 `online-boutique` 命名空间中的 Online-Boutique 服务。
3. 接入新增 `coupon-service` 和 `inventory-service` 的 Prometheus `/metrics`。
4. 确认 CPU、内存、Pod 状态、请求量、错误率、延迟、网络流量等指标。
5. 制作 Grafana 看板并保存截图。

## 2. 前置条件

部署监控前先确认：

```bash
bash scripts/check_env.sh
bash scripts/start_minikube.sh
bash scripts/deploy_online_boutique.sh
kubectl get pods -n online-boutique
```

如果 Docker daemon 不可访问，需要先启动 Docker Desktop。若 Online-Boutique Pod 长时间处于 `ContainerCreating` 或 `ImagePullBackOff`，优先检查镜像仓库网络访问。

## 3. 部署监控组件

本项目使用 Helm 安装 `kube-prometheus-stack`，其中包含：

| 组件 | 用途 |
|---|---|
| Prometheus | 采集和查询指标 |
| Grafana | 展示监控看板 |
| kube-state-metrics | 提供 Kubernetes 对象状态指标 |
| node-exporter | 提供节点资源指标 |
| Alertmanager | 预留告警能力 |

部署命令：

```bash
bash scripts/deploy_monitoring.sh
```

默认配置：

| 项目 | 默认值 |
|---|---|
| Namespace | `monitoring` |
| Helm release | `monitoring-stack` |
| Grafana 本地地址 | `http://localhost:3000` |
| Prometheus 本地地址 | `http://localhost:9090` |

## 4. 访问 Prometheus

启动端口转发：

```bash
bash scripts/port_forward_prometheus.sh
```

浏览器访问：

```text
http://localhost:9090
```

在 Prometheus 页面打开 `Status -> Targets`，确认以下目标为 `UP`：

1. kubelet / cAdvisor
2. kube-state-metrics
3. node-exporter
4. Prometheus 自身
5. `coupon-service` 和 `inventory-service`

建议截图保存到：

```text
figures/monitoring/prometheus_targets.png
```

## 5. 访问 Grafana

启动端口转发：

```bash
bash scripts/port_forward_grafana.sh
```

浏览器访问：

```text
http://localhost:3000
```

默认账号：

```text
admin
```

查询默认密码：

```bash
kubectl get secret -n monitoring monitoring-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

部署脚本会把 `monitoring/grafana/dashboards/online-boutique-overview.json` 创建为 Grafana dashboard ConfigMap。进入 Grafana 后查看：

```text
Online Boutique / Online Boutique Monitoring Overview
```

建议截图保存到：

```text
figures/monitoring/grafana_overview.png
figures/monitoring/grafana_coupon_inventory.png
figures/monitoring/grafana_fault_compare.png
```

## 6. Online-Boutique 指标接入

`kube-prometheus-stack` 默认可以采集 Kubernetes 和容器层指标，因此 Online-Boutique 即使没有应用级 `/metrics`，也可以查看：

| 指标 | 数据来源 |
|---|---|
| Pod 状态 | kube-state-metrics |
| Pod 重启次数 | kube-state-metrics |
| CPU 使用率 | kubelet / cAdvisor |
| 内存使用量 | kubelet / cAdvisor |
| 网络接收/发送流量 | kubelet / cAdvisor |

请求量、错误率、请求延迟属于应用级指标。Online-Boutique 原始服务如果没有稳定暴露 Prometheus 指标端点，本项目用新增的 `coupon-service` 和 `inventory-service` 提供 `/metrics`，补齐请求速率、错误率、平均延迟和 P95 延迟展示。

## 7. 新增微服务接入规范

`coupon-service` 和 `inventory-service` 需要按以下约定接入 Prometheus。

Service 需要添加 label：

```yaml
metadata:
  labels:
    monitoring: enabled
```

Service 需要暴露名为 `http` 的端口：

```yaml
ports:
  - name: http
    port: 8080
    targetPort: 8080
```

服务自身需要提供：

```text
GET /metrics
```

推荐指标：

| 指标 | 说明 |
|---|---|
| `coupon_service_requests_total` | coupon-service 请求总数，包含 `method`、`endpoint`、`status` 标签 |
| `coupon_service_request_duration_seconds_bucket` | coupon-service 请求耗时 histogram |
| `inventory_service_requests_total` | inventory-service 请求总数，包含 `method`、`endpoint`、`status` 标签 |
| `inventory_service_request_duration_seconds_bucket` | inventory-service 请求耗时 histogram |

本仓库已提供 `monitoring/prometheus/servicemonitor-custom-services.yaml`，会自动采集 `online-boutique` 命名空间中带有 `monitoring: enabled` label 的 Service。

## 8. PromQL 查询清单

完整查询记录见：

```text
results/monitoring/promql_queries.md
```

常用查询：

```promql
sum by (phase) (kube_pod_status_phase{namespace="online-boutique"})
```

```promql
sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="online-boutique"}[5m]))
```

```promql
sum by (pod) (container_memory_working_set_bytes{namespace="online-boutique"})
```

```promql
sum by (service) (rate({__name__=~"coupon_service_requests_total|inventory_service_requests_total", namespace="online-boutique"}[5m]))
```

```promql
histogram_quantile(0.95, sum by (le, service) (rate({__name__=~"coupon_service_request_duration_seconds_bucket|inventory_service_request_duration_seconds_bucket", namespace="online-boutique"}[5m])))
```

## 9. 数据导出

正常流量场景由 E 提供访问流量后执行：

```bash
python3 scripts/export_monitoring_metrics.py \
  --experiment-id EXP_001 \
  --scenario normal_traffic \
  --output data/raw/normal_metrics.csv
```

故障注入场景由 D 注入故障、E 提供访问流量后执行：

```bash
python3 scripts/export_monitoring_metrics.py \
  --experiment-id EXP_002 \
  --scenario fault_traffic \
  --output data/raw/fault_metrics_raw.csv
```

CSV 字段说明见：

```text
results/monitoring/metrics_description.md
```

## 10. 验收标准

完成监控模块后需要确认：

1. `kubectl get pods -n monitoring` 中 Prometheus、Grafana、kube-state-metrics、node-exporter 正常运行。
2. Prometheus Targets 页面核心 target 为 `UP`。
3. Prometheus 可以查询 Online-Boutique 的 Pod 状态、CPU、内存、网络指标。
4. Grafana 可以打开 `Online Boutique Monitoring Overview` 看板。
5. 看板中资源类面板有数据。
6. `coupon-service` 和 `inventory-service` 的请求量、错误率、平均延迟、P95 延迟面板有数据。
7. 截图保存为 `prometheus_targets.png`、`grafana_overview.png`、`grafana_coupon_inventory.png`、`grafana_fault_compare.png`。
8. PromQL 查询记录保存到 `results/monitoring/promql_queries.md`。
9. 正常数据保存到 `data/raw/normal_metrics.csv`。
10. 故障数据保存到 `data/raw/fault_metrics_raw.csv`。

## 11. 当前限制

当前 CSV 导出脚本依赖 Prometheus 本地端口转发地址 `http://localhost:9090`。导出前需要先执行 `bash scripts/port_forward_prometheus.sh`。

Online-Boutique 原始服务的 Kubernetes 资源指标已经可以通过 `kube-prometheus-stack` 采集；原系统的 HTTP/gRPC 请求量、错误率和延迟如果需要更细粒度追踪，仍需要额外接入 OpenTelemetry 或 Prometheus instrumentation。
