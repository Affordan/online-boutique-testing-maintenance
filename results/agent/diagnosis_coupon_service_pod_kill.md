# AIOps Agent 诊断报告

## 诊断结论

检测到 `coupon-service` 存在 `pod_kill` 类型异常，严重程度为 `high`。

## 疑似异常服务

coupon-service

## 根因分类

pod_kill

## 异常证据

- restart_count 从正常均值 0.0000 上升为 0.1213
- error_rate 从正常均值 0.0011 上升到 0.0139，约为正常的 12.63 倍
- avg_latency_ms 从正常均值 1.1940 上升到 1.7901，约为正常的 1.50 倍
- p90_latency_ms 从正常均值 1.8793 上升到 3.3545，约为正常的 1.78 倍
- p95_latency_ms 从正常均值 2.2731 上升到 4.7644，约为正常的 2.10 倍
- p99_latency_ms 从正常均值 3.1106 上升到 7.9561，约为正常的 2.56 倍
- throughput 从正常均值 333.0306 下降到 294.0801，约为正常的 0.88 倍
- http_5xx_rate 从正常均值 0.0599 上升到 3.3322，约为正常的 55.65 倍
- 异常阶段与故障窗口 `during_fault` 匹配

## 影响范围

可能影响下游服务：`frontend`、`checkoutservice`

## 建议

- 确认 coupon-service Deployment 副本数和重启次数
- 检查是否存在 ChaosMesh PodChaos 或节点资源驱逐
- 检查 coupon-service Pod 状态、事件和最近日志
- 对照 Grafana 看板确认故障结束后指标是否回落

## 候选人工确认命令

```bash
kubectl get pods -n online-boutique -l app=coupon-service
```
```bash
kubectl logs -n online-boutique deploy/coupon-service --tail=80
```
```bash
kubectl describe deployment coupon-service -n online-boutique
```
```bash
# 人工确认后可选: kubectl rollout restart deployment/coupon-service -n online-boutique
```
