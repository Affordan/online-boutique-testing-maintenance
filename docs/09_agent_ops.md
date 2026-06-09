# 智能运维 Agent 实现说明

本文记录 Online-Boutique 项目中 AIOps Agent 的实现范围、运行方式、诊断逻辑和输出结果。

## 1. 实现范围

本项目实现的是轻量级智能运维 Agent，重点完成以下能力：

1. 读取正常状态与故障状态监控数据。
2. 识别异常服务和异常指标。
3. 对异常进行根因分类。
4. 生成 Markdown 诊断报告和 JSON 汇总结果。
5. 输出候选人工确认命令。

Agent 不自动执行故障注入，也不自动执行恢复操作。ChaosMesh 故障实验由独立实验模块完成，Agent 读取已有数据并进行诊断分析。为了避免误操作 Kubernetes 集群，恢复命令只作为建议输出，由人工确认后执行。

## 2. 文件结构

```text
agent/
├── README.md
├── requirements.txt
├── run_agent.py
├── config.yaml
├── service_topology.yaml
└── aiops_agent/
    ├── agent.py
    ├── anomaly_detector.py
    ├── data_loader.py
    ├── models.py
    ├── report_writer.py
    └── root_cause_classifier.py
```

输出结果：

```text
results/agent/
├── diagnosis_coupon_service_pod_kill.md
├── diagnosis_frontend_network_delay.md
├── diagnosis_checkoutservice_memory_stress.md
├── diagnosis_productcatalogservice_cpu_stress.md
└── diagnosis_summary.json
```

## 3. 输入数据

Agent 默认读取：

```text
data/raw/normal_metrics.csv
data/raw/fault_metrics.csv
```

这两份文件字段完全一致，均覆盖 14 个服务、5 次 run、5 秒采样间隔。Agent 主要使用以下指标：

```text
cpu_usage
memory_usage_mb
restart_count
request_rate
error_rate
avg_latency_ms
p90_latency_ms
p95_latency_ms
p99_latency_ms
throughput
http_5xx_rate
network_receive_bytes
network_transmit_bytes
```

## 4. 运行命令

运行全部诊断：

```powershell
python agent\run_agent.py --case all --max-reports 4
```

运行指定服务案例：

```powershell
python agent\run_agent.py --case inventory_network_delay --max-reports 1
python agent\run_agent.py --case coupon_cpu_stress --max-reports 1
python agent\run_agent.py --case frontend_pod_kill --max-reports 1
```

说明：指定案例只用于选择服务范围，最终根因分类仍然以数据中的指标证据和 `fault_service`、`fault_type` 标注为准，不硬编码结论。

## 5. 异常检测逻辑

Agent 以服务为粒度对比 normal 与 fault 窗口的均值变化：

| 异常类型 | 判断依据 |
|---|---|
| CPU 异常 | `cpu_usage` 相对 normal 明显升高 |
| 内存异常 | `memory_usage_mb` 相对 normal 明显升高 |
| Pod 重启 | `restart_count` 出现实际增加 |
| 请求失败 | `error_rate` 或 `http_5xx_rate` 明显升高 |
| 延迟异常 | `avg_latency_ms`、`p95_latency_ms`、`p99_latency_ms` 明显升高 |
| 吞吐下降 | `throughput` 相对 normal 明显下降 |
| 网络异常 | 网络收发指标变化并伴随延迟升高 |

检测结果按异常分数排序，默认输出最明显的前几个服务。

## 6. 根因分类

Agent 将异常归入以下类别：

| 根因类别 | 典型证据 |
|---|---|
| `pod_kill` | `restart_count` 增加，5xx 或错误率升高 |
| `cpu_stress` | CPU 与延迟同步升高 |
| `memory_stress` | 内存升高或故障标注显示内存压力 |
| `network_delay` | P95/P99 延迟明显升高，故障标注显示网络延迟 |
| `service_error` | 错误率或 5xx 升高但无更明确资源类证据 |

当数据中存在 `fault_service` 与 `fault_type` 标注时，Agent 会优先使用被注入服务的真实故障类型作为根因参考，再结合指标变化生成证据。

## 7. 诊断结果

当前全量运行输出了 4 个诊断报告：

| 服务 | 根因分类 | 严重程度 |
|---|---|---|
| `coupon-service` | `pod_kill` | high |
| `frontend` | `network_delay` | high |
| `checkoutservice` | `memory_stress` | high |
| `productcatalogservice` | `cpu_stress` | high |

每份报告包含：

1. 诊断结论。
2. 疑似异常服务。
3. 根因分类。
4. 异常证据。
5. 影响范围。
6. 运维建议。
7. 候选人工确认命令。

## 8. 安全策略

Agent 默认采用保守运维策略：

- 不自动执行 `kubectl rollout restart`。
- 不自动删除 Pod。
- 不自动扩缩容 Deployment。
- 只输出候选命令，交由人工确认。

这样既能展示智能运维中的异常检测和根因定位能力，又能避免在答辩或演示环境中误操作集群。
