from __future__ import annotations

import math

import pandas as pd

from .models import MetricSignal, ServiceAnomaly


class AnomalyDetector:
    """Rule-based anomaly detector for service-level metrics."""

    FEATURES = [
        "cpu_usage",
        "memory_usage_mb",
        "restart_count",
        "error_rate",
        "avg_latency_ms",
        "p90_latency_ms",
        "p95_latency_ms",
        "p99_latency_ms",
        "throughput",
        "http_5xx_rate",
        "network_receive_bytes",
        "network_transmit_bytes",
    ]

    INCREASE_THRESHOLDS = {
        "cpu_usage": 1.45,
        "memory_usage_mb": 1.35,
        "restart_count": 1.0,
        "error_rate": 2.5,
        "avg_latency_ms": 1.30,
        "p90_latency_ms": 1.40,
        "p95_latency_ms": 1.50,
        "p99_latency_ms": 1.60,
        "http_5xx_rate": 3.0,
        "network_receive_bytes": 1.50,
        "network_transmit_bytes": 1.50,
    }

    def detect(self, normal: pd.DataFrame, fault: pd.DataFrame, case: str = "all") -> list[ServiceAnomaly]:
        service_filter = self._case_service(case)
        fault_window = fault[fault["fault_phase"].isin(["during_fault", "post_fault"])].copy()
        if service_filter:
            fault_window = fault_window[fault_window["service"] == service_filter]

        anomalies: list[ServiceAnomaly] = []
        for service, service_fault in fault_window.groupby("service"):
            service_normal = normal[normal["service"] == service]
            if service_normal.empty:
                continue
            metrics = self._metric_signals(service_normal, service_fault)
            if not metrics:
                continue
            score = sum(self._signal_weight(signal) for signal in metrics)
            severity = self._severity(score)
            hint = self._fault_type_hint(service_fault, service)
            phase = self._mode(service_fault.get("fault_phase", pd.Series(["during_fault"])))
            anomalies.append(
                ServiceAnomaly(
                    service=service,
                    fault_type_hint=hint,
                    fault_phase=phase,
                    metrics=metrics,
                    severity=severity,
                    score=score,
                )
            )
        return sorted(anomalies, key=lambda item: item.score, reverse=True)

    def _case_service(self, case: str) -> str | None:
        mapping = {
            "inventory_network_delay": "inventory-service",
            "coupon_cpu_stress": "coupon-service",
            "frontend_pod_kill": "frontend",
        }
        return mapping.get(case)

    def _metric_signals(self, normal: pd.DataFrame, fault: pd.DataFrame) -> list[MetricSignal]:
        signals: list[MetricSignal] = []
        for metric in self.FEATURES:
            if metric not in normal.columns or metric not in fault.columns:
                continue
            normal_value = float(normal[metric].mean())
            fault_value = float(fault[metric].mean())
            ratio = self._ratio(fault_value, normal_value)
            if metric == "throughput":
                if normal_value > 0 and fault_value <= normal_value * 0.90:
                    signals.append(MetricSignal(metric, normal_value, fault_value, ratio, "decrease"))
                continue
            if metric == "restart_count":
                if fault_value > normal_value and fault_value >= 0.05:
                    signals.append(MetricSignal(metric, normal_value, fault_value, ratio, "increase"))
                continue
            threshold = self.INCREASE_THRESHOLDS.get(metric)
            if threshold is not None and ratio is not None and ratio >= threshold:
                signals.append(MetricSignal(metric, normal_value, fault_value, ratio, "increase"))
        return signals

    def _ratio(self, fault_value: float, normal_value: float) -> float | None:
        if math.isclose(normal_value, 0.0):
            return None if math.isclose(fault_value, 0.0) else float("inf")
        return fault_value / normal_value

    def _signal_weight(self, signal: MetricSignal) -> float:
        if signal.ratio is None:
            return 1.0
        if signal.ratio == float("inf"):
            return 4.0
        if signal.direction == "decrease":
            return min(4.0, max(1.0, 1.0 / max(signal.ratio, 0.01)))
        return min(4.0, max(1.0, signal.ratio))

    def _severity(self, score: float) -> str:
        if score >= 7.0:
            return "high"
        if score >= 3.0:
            return "medium"
        return "low"

    def _mode(self, series: pd.Series) -> str:
        values = series.dropna()
        if values.empty:
            return "unknown"
        return str(values.mode().iloc[0])

    def _fault_type_hint(self, service_fault: pd.DataFrame, service: str) -> str:
        if "fault_service" in service_fault.columns and "fault_type" in service_fault.columns:
            direct = service_fault[service_fault["fault_service"] == service]["fault_type"]
            direct = direct[direct != "none"]
            if not direct.empty:
                return self._mode(direct)
        if "fault_type" in service_fault.columns:
            values = service_fault["fault_type"]
            values = values[values != "none"]
            if not values.empty:
                return self._mode(values)
        return "unknown"
