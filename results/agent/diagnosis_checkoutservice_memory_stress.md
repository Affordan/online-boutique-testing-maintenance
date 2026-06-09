# AIOps Agent 诊断报告

## 诊断结论

检测到 `checkoutservice` 存在 `memory_stress` 类型异常，严重程度为 `high`。

## 疑似异常服务

checkoutservice

## 根因分类

memory_stress

## 异常证据

- error_rate 从正常均值 0.0011 上升到 0.0088，约为正常的 8.08 倍
- avg_latency_ms 从正常均值 48.2724 上升到 79.3429，约为正常的 1.64 倍
- p90_latency_ms 从正常均值 76.0839 上升到 151.7600，约为正常的 1.99 倍
- p95_latency_ms 从正常均值 91.6658 上升到 224.2274，约为正常的 2.45 倍
- p99_latency_ms 从正常均值 125.3891 上升到 385.5486，约为正常的 3.07 倍
- throughput 从正常均值 132.0125 下降到 117.2841，约为正常的 0.89 倍
- http_5xx_rate 从正常均值 0.0226 上升到 0.9454，约为正常的 41.87 倍
- 异常阶段与故障窗口 `during_fault` 匹配

## 影响范围

可能影响下游服务：`paymentservice`、`shippingservice`、`emailservice`、`cartservice`

## 建议

- 检查 checkoutservice 内存 limit/request 和 OOMKilled 事件
- 观察内存曲线是否持续上升，必要时扩大内存限制
- 检查 checkoutservice Pod 状态、事件和最近日志
- 对照 Grafana 看板确认故障结束后指标是否回落

## 候选人工确认命令

```bash
kubectl get pods -n online-boutique -l app=checkoutservice
```
```bash
kubectl logs -n online-boutique deploy/checkoutservice --tail=80
```
```bash
kubectl describe deployment checkoutservice -n online-boutique
```
```bash
# 人工确认后可选: kubectl rollout restart deployment/checkoutservice -n online-boutique
```
