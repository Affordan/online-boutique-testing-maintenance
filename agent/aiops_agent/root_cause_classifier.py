from __future__ import annotations

import pandas as pd

from .models import Diagnosis, ServiceAnomaly


class RootCauseClassifier:
    """Classify anomalies into AIOps root-cause categories."""

    TOPOLOGY = {
        "frontend": ["checkoutservice", "productcatalogservice", "cartservice", "recommendationservice"],
        "checkoutservice": ["paymentservice", "shippingservice", "emailservice", "cartservice"],
        "coupon-service": ["frontend", "checkoutservice"],
        "inventory-service": ["frontend", "productcatalogservice", "checkoutservice"],
        "productcatalogservice": ["frontend", "recommendationservice"],
    }

    def classify(self, anomaly: ServiceAnomaly, normal: pd.DataFrame, fault: pd.DataFrame) -> Diagnosis:
        metric_names = {signal.metric for signal in anomaly.metrics}
        root_cause = self._root_cause(metric_names, anomaly.fault_type_hint)
        evidence = self._evidence(anomaly)
        recommendations = self._recommendations(anomaly.service, root_cause)
        commands = self._candidate_commands(anomaly.service, root_cause)
        return Diagnosis(
            service=anomaly.service,
            root_cause=root_cause,
            severity=anomaly.severity,
            score=anomaly.score,
            evidence=evidence,
            recommendations=recommendations,
            affected_services=self.TOPOLOGY.get(anomaly.service, []),
            candidate_commands=commands,
        )

    def _root_cause(self, metrics: set[str], hint: str) -> str:
        if "restart_count" in metrics:
            return "pod_kill"
        if hint in {"cpu_stress", "memory_stress", "network_delay", "pod_kill"}:
            return hint
        if "cpu_usage" in metrics and {"avg_latency_ms", "p95_latency_ms", "p99_latency_ms"} & metrics:
            return "cpu_stress"
        if "memory_usage_mb" in metrics:
            return "memory_stress"
        if {"p95_latency_ms", "p99_latency_ms"} & metrics and {"network_receive_bytes", "network_transmit_bytes"} & metrics:
            return "network_delay"
        if {"error_rate", "http_5xx_rate"} & metrics:
            return "service_error"
        if {"avg_latency_ms", "p95_latency_ms", "p99_latency_ms"} & metrics:
            return "network_delay"
        return "service_error"

    def _evidence(self, anomaly: ServiceAnomaly) -> list[str]:
        evidence = []
        for signal in anomaly.metrics:
            if signal.ratio == float("inf"):
                evidence.append(f"{signal.metric} 从正常均值 {signal.normal_value:.4f} 上升为 {signal.fault_value:.4f}")
            elif signal.ratio is None:
                evidence.append(f"{signal.metric} 出现异常变化，故障均值为 {signal.fault_value:.4f}")
            elif signal.direction == "decrease":
                evidence.append(
                    f"{signal.metric} 从正常均值 {signal.normal_value:.4f} 下降到 {signal.fault_value:.4f}，约为正常的 {signal.ratio:.2f} 倍"
                )
            else:
                evidence.append(
                    f"{signal.metric} 从正常均值 {signal.normal_value:.4f} 上升到 {signal.fault_value:.4f}，约为正常的 {signal.ratio:.2f} 倍"
                )
        evidence.append(f"异常阶段与故障窗口 `{anomaly.fault_phase}` 匹配")
        return evidence

    def _recommendations(self, service: str, root_cause: str) -> list[str]:
        common = [
            f"检查 {service} Pod 状态、事件和最近日志",
            "对照 Grafana 看板确认故障结束后指标是否回落",
        ]
        by_cause = {
            "pod_kill": [
                f"确认 {service} Deployment 副本数和重启次数",
                "检查是否存在 ChaosMesh PodChaos 或节点资源驱逐",
            ],
            "cpu_stress": [
                f"检查 {service} CPU limit/request 和容器 CPU 使用率",
                "降低压测流量或扩容对应 Deployment 后观察延迟是否恢复",
            ],
            "memory_stress": [
                f"检查 {service} 内存 limit/request 和 OOMKilled 事件",
                "观察内存曲线是否持续上升，必要时扩大内存限制",
            ],
            "network_delay": [
                f"检查 {service} 与上下游服务之间的网络延迟",
                "核对 ChaosMesh NetworkChaos 配置和服务调用链路",
            ],
            "service_error": [
                f"检查 {service} 业务接口错误日志和 5xx 响应",
                "优先回滚最近变更或降低流量后确认错误率",
            ],
        }
        return by_cause.get(root_cause, by_cause["service_error"]) + common

    def _candidate_commands(self, service: str, root_cause: str) -> list[str]:
        return [
            f"kubectl get pods -n online-boutique -l app={service}",
            f"kubectl logs -n online-boutique deploy/{service} --tail=80",
            f"kubectl describe deployment {service} -n online-boutique",
            f"# 人工确认后可选: kubectl rollout restart deployment/{service} -n online-boutique",
        ]
