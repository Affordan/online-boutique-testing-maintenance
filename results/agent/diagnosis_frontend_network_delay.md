# AIOps Agent 诊断报告

## 诊断结论

检测到 `frontend` 存在 `network_delay` 类型异常，严重程度为 `high`。

## 疑似异常服务

frontend

## 根因分类

network_delay

## 异常证据

- error_rate 从正常均值 0.0011 上升到 0.0096，约为正常的 8.69 倍
- avg_latency_ms 从正常均值 18.0740 上升到 37.2369，约为正常的 2.06 倍
- p90_latency_ms 从正常均值 28.4665 上升到 71.5367，约为正常的 2.51 倍
- p95_latency_ms 从正常均值 34.3432 上升到 107.5956，约为正常的 3.13 倍
- p99_latency_ms 从正常均值 47.0103 上升到 188.1967，约为正常的 4.00 倍
- throughput 从正常均值 476.9630 下降到 420.5349，约为正常的 0.88 倍
- http_5xx_rate 从正常均值 0.0858 上升到 3.8094，约为正常的 44.38 倍
- 异常阶段与故障窗口 `during_fault` 匹配

## 影响范围

可能影响下游服务：`checkoutservice`、`productcatalogservice`、`cartservice`、`recommendationservice`

## 建议

- 检查 frontend 与上下游服务之间的网络延迟
- 核对 ChaosMesh NetworkChaos 配置和服务调用链路
- 检查 frontend Pod 状态、事件和最近日志
- 对照 Grafana 看板确认故障结束后指标是否回落

## 候选人工确认命令

```bash
kubectl get pods -n online-boutique -l app=frontend
```
```bash
kubectl logs -n online-boutique deploy/frontend --tail=80
```
```bash
kubectl describe deployment frontend -n online-boutique
```
```bash
# 人工确认后可选: kubectl rollout restart deployment/frontend -n online-boutique
```
