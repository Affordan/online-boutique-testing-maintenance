# Prometheus + Grafana 监控部署记录

本文记录 Online-Boutique 微服务系统的监控组件部署、指标接入、PromQL 查询和 Grafana 看板验证方式。

## 1. 目标

监控实验需要完成以下内容：

1. 部署 Prometheus 和 Grafana。
2. 接入 `online-boutique` 命名空间中的 Online-Boutique 服务。
3. 为后续新增微服务预留 Prometheus `/metrics` 接入规范。
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
5. 已接入的新增微服务

建议截图保存到：

```text
figures/monitoring/01_prometheus_targets.png
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
figures/monitoring/02_grafana_overview.png
figures/monitoring/03_resource_metrics.png
figures/monitoring/04_request_metrics.png
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

请求量、错误率、请求延迟属于应用级指标。Online-Boutique 原始服务如果没有稳定暴露 Prometheus 指标端点，需要通过后续新增微服务或额外 instrumentation 补齐。

## 7. 新增微服务接入规范

`ops-alert-service` 和 `user-log-service` 落地后，建议按以下约定接入 Prometheus。

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
    port: 8000
    targetPort: 8000
```

服务自身需要提供：

```text
GET /metrics
```

推荐指标：

| 指标 | 说明 |
|---|---|
| `http_requests_total` | 请求总数，包含 `service`、`method`、`path`、`status` 标签 |
| `http_request_duration_seconds_bucket` | 请求耗时 histogram |
| `http_request_duration_seconds_count` | 请求耗时样本数 |
| `http_request_duration_seconds_sum` | 请求耗时总和 |
| `service_health` | 服务健康状态，1 表示正常，0 表示异常 |

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
sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="online-boutique", container!="", image!=""}[5m]))
```

```promql
sum by (pod) (container_memory_working_set_bytes{namespace="online-boutique", container!="", image!=""})
```

```promql
sum by (service) (rate(http_requests_total{namespace="online-boutique"}[5m]))
```

```promql
histogram_quantile(0.95, sum by (le, service) (rate(http_request_duration_seconds_bucket{namespace="online-boutique"}[5m])))
```

## 9. 验收标准

完成监控模块后需要确认：

1. `kubectl get pods -n monitoring` 中 Prometheus、Grafana、kube-state-metrics、node-exporter 正常运行。
2. Prometheus Targets 页面核心 target 为 `UP`。
3. Prometheus 可以查询 Online-Boutique 的 Pod 状态、CPU、内存、网络指标。
4. Grafana 可以打开 `Online Boutique Monitoring Overview` 看板。
5. 看板中资源类面板有数据。
6. 如果新增微服务已实现，请求量、错误率、P95 延迟面板有数据。
7. 截图保存到 `figures/monitoring/`。
8. PromQL 查询记录保存到 `results/monitoring/promql_queries.md`。

## 10. 当前限制

截至当前版本，仓库中的 `services/` 目录仍是占位状态，`ops-alert-service` 和 `user-log-service` 尚未实现。因此请求量、错误率、延迟等应用级指标需要等新增微服务暴露 `/metrics` 后才能完整展示。

Online-Boutique 原始服务的 Kubernetes 资源指标已经可以通过 `kube-prometheus-stack` 采集；若后续需要完整追踪原始服务的 HTTP/gRPC 请求量、错误率和延迟，需要为服务补充应用级指标或接入 OpenTelemetry/Prometheus instrumentation。
