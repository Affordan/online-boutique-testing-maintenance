# AIOps Agent

本目录实现 Online-Boutique 项目的轻量级智能运维 Agent。Agent 不自动执行故障注入或恢复操作，而是读取已交付的监控 CSV，完成异常检测、根因分类和诊断报告生成。

## 功能

1. 读取 `data/raw/normal_metrics.csv` 和 `data/raw/fault_metrics.csv`。
2. 对比正常窗口与故障窗口的 CPU、内存、重启、错误率、延迟、吞吐和网络指标。
3. 将异常归因为 `pod_kill`、`cpu_stress`、`memory_stress`、`network_delay` 或 `service_error`。
4. 输出 Markdown 诊断报告和 `diagnosis_summary.json`。
5. 仅给出候选人工确认命令，不自动重启或修改 Kubernetes 集群。

## 运行

```powershell
python agent\run_agent.py --case all
```

指定案例：

```powershell
python agent\run_agent.py --case inventory_network_delay
python agent\run_agent.py --case coupon_cpu_stress
python agent\run_agent.py --case frontend_pod_kill
```

输出目录：

```text
results/agent/
```

## 安全策略

Agent 默认运行在安全模式下，只生成诊断结论、证据、建议和候选命令。涉及 `kubectl rollout restart` 等恢复操作时，报告中只打印命令，由人工确认后执行。
