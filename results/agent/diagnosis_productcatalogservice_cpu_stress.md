# AIOps Agent 诊断报告

## 诊断结论

检测到 `productcatalogservice` 存在 `cpu_stress` 类型异常，严重程度为 `high`。

## 疑似异常服务

productcatalogservice

## 根因分类

cpu_stress

## 异常证据

- avg_latency_ms 从正常均值 6.5217 上升到 10.4483，约为正常的 1.60 倍
- p90_latency_ms 从正常均值 10.2708 上升到 19.5190，约为正常的 1.90 倍
- p95_latency_ms 从正常均值 12.3947 上升到 28.5756，约为正常的 2.31 倍
- p99_latency_ms 从正常均值 16.9627 上升到 48.4161，约为正常的 2.85 倍
- http_5xx_rate 从正常均值 0.0514 上升到 0.3586，约为正常的 6.98 倍
- 异常阶段与故障窗口 `during_fault` 匹配

## 影响范围

可能影响下游服务：`frontend`、`recommendationservice`

## 建议

- 检查 productcatalogservice CPU limit/request 和容器 CPU 使用率
- 降低压测流量或扩容对应 Deployment 后观察延迟是否恢复
- 检查 productcatalogservice Pod 状态、事件和最近日志
- 对照 Grafana 看板确认故障结束后指标是否回落

## 候选人工确认命令

```bash
kubectl get pods -n online-boutique -l app=productcatalogservice
```
```bash
kubectl logs -n online-boutique deploy/productcatalogservice --tail=80
```
```bash
kubectl describe deployment productcatalogservice -n online-boutique
```
```bash
# 人工确认后可选: kubectl rollout restart deployment/productcatalogservice -n online-boutique
```
