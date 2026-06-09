# Monitoring Metrics Description

本文说明最终交付的 `normal_metrics.csv`、`fault_metrics.csv` 与 `all_metrics_labeled.csv` 的字段、单位和使用方式，供后续异常检测建模、根因定位和可视化分析使用。

本次数据采集与整理由王秀强、邱俊杰、段坤良共同完成：邱俊杰负责 Prometheus/Grafana 指标接入，段坤良负责 ChaosMesh 故障注入和故障窗口记录，王秀强负责字段统一、数据质量校验、统计报告和最终集成。

## 1. 文件说明

| 文件 | label | 说明 |
|---|---:|---|
| `data/raw/normal_metrics.csv` | 0 | 系统正常运行状态下的监控数据 |
| `data/raw/fault_metrics.csv` | 1 | 故障注入实验前、中、后窗口的监控数据 |
| `data/raw/all_metrics_labeled.csv` | 0/1 | normal 与 fault 合并后的算法建模数据 |

三份文件字段顺序一致。`normal_metrics.csv` 与 `fault_metrics.csv` 均为 25,200 行，覆盖 14 个服务、5 次 run、5 秒固定采样间隔、单次 run 30 分钟。

## 2. 字段说明

| 字段名 | 单位/类型 | 说明 |
|---|---|---|
| `timestamp` | datetime | 采样时间，格式为 `YYYY-MM-DD HH:MM:SS` |
| `relative_time_sec` | second | 距离本次 run 开始的秒数，用于对齐多次实验 |
| `experiment_id` | string | 实验编号，例如 `EXP_NORMAL_01`、`EXP_FAULT_01` |
| `run_id` | string | 重复实验编号，例如 `RUN_01` |
| `scenario` | string | 场景，normal 为 `normal_traffic`，fault 为故障类型 |
| `label` | int | 正常为 0，故障为 1 |
| `service` | string | 服务名 |
| `pod` | string | Pod 名称 |
| `namespace` | string | Kubernetes namespace，当前为 `online-boutique` |
| `node` | string | Pod 所在节点 |
| `cpu_usage` | core/s | CPU 使用率或 CPU 使用速率 |
| `memory_usage_mb` | MB | 内存使用量 |
| `restart_count` | count | 容器重启次数 |
| `request_rate` | req/s | 每秒请求数 |
| `error_rate` | ratio | 错误率，约等于 `(4xx + 5xx) / request_rate` |
| `avg_latency_ms` | ms | 平均响应时间 |
| `p50_latency_ms` | ms | P50 响应时间 |
| `p90_latency_ms` | ms | P90 响应时间 |
| `p95_latency_ms` | ms | P95 响应时间 |
| `p99_latency_ms` | ms | P99 响应时间 |
| `throughput` | req/s | 有效吞吐量 |
| `http_2xx_rate` | req/s | 2xx 响应速率 |
| `http_4xx_rate` | req/s | 4xx 响应速率 |
| `http_5xx_rate` | req/s | 5xx 响应速率 |
| `network_receive_bytes` | bytes/s | 网络接收速率 |
| `network_transmit_bytes` | bytes/s | 网络发送速率 |
| `fault_type` | string | 故障类型；normal 为 `none` |
| `fault_service` | string | 被注入故障的服务；normal 为 `none` |
| `fault_start_time` | datetime/string | 故障开始时间；normal 为 `none` |
| `fault_end_time` | datetime/string | 故障结束时间；normal 为 `none` |
| `fault_phase` | string | `normal`、`pre_fault`、`during_fault`、`post_fault` |

## 3. 故障类型

`fault_metrics.csv` 覆盖以下故障：

| fault_type | 观察重点 |
|---|---|
| `pod_kill` | `restart_count`、`http_5xx_rate`、`error_rate`、延迟和恢复过程 |
| `cpu_stress` | `cpu_usage`、延迟、吞吐变化 |
| `memory_stress` | `memory_usage_mb`、重启、延迟变化 |
| `network_delay` | `avg_latency_ms`、`p95_latency_ms`、`p99_latency_ms` 明显上升 |

## 4. 建模使用说明

推荐作为模型输入的数值特征：

```text
cpu_usage
memory_usage_mb
restart_count
request_rate
error_rate
avg_latency_ms
p50_latency_ms
p90_latency_ms
p95_latency_ms
p99_latency_ms
throughput
http_2xx_rate
http_4xx_rate
http_5xx_rate
network_receive_bytes
network_transmit_bytes
```

不要作为模型输入的字段：

```text
timestamp
experiment_id
run_id
scenario
label
fault_type
fault_service
fault_start_time
fault_end_time
fault_phase
pod
namespace
node
```

这些字段只能用于分组、标注、画图和结果解释。直接作为输入特征会导致标签泄漏。

## 5. 质量验收

最终质量验收见：

```text
results/monitoring/data_delivery_validation.md
results/monitoring/dataset_overview.csv
results/monitoring/normal_metrics_stat_summary.csv
results/monitoring/fault_metrics_stat_summary.csv
results/monitoring/metric_variation_comparison.csv
```
