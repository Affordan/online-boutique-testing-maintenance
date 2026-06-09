from __future__ import annotations

from pathlib import Path

import pandas as pd


class MetricsDataLoader:
    """Load and validate normal/fault monitoring CSV files."""

    def __init__(self, normal_path: str | Path, fault_path: str | Path) -> None:
        self.normal_path = Path(normal_path)
        self.fault_path = Path(fault_path)

    def load(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        normal = pd.read_csv(self.normal_path)
        fault = pd.read_csv(self.fault_path)
        self._validate_schema(normal, fault)
        self._validate_labels(normal, fault)
        self._normalize_types(normal)
        self._normalize_types(fault)
        return normal, fault

    def _validate_schema(self, normal: pd.DataFrame, fault: pd.DataFrame) -> None:
        if list(normal.columns) != list(fault.columns):
            raise ValueError("normal/fault schema mismatch")
        required = {
            "timestamp",
            "service",
            "label",
            "fault_type",
            "fault_phase",
            "cpu_usage",
            "memory_usage_mb",
            "restart_count",
            "request_rate",
            "error_rate",
            "avg_latency_ms",
            "p95_latency_ms",
            "p99_latency_ms",
            "throughput",
            "http_5xx_rate",
        }
        missing = sorted(required - set(normal.columns))
        if missing:
            raise ValueError(f"schema missing required fields: {missing}")

    def _validate_labels(self, normal: pd.DataFrame, fault: pd.DataFrame) -> None:
        if set(normal["label"].unique()) != {0}:
            raise ValueError("normal_metrics.csv must contain only label=0")
        if set(fault["label"].unique()) != {1}:
            raise ValueError("fault_metrics.csv must contain only label=1")
        if set(normal["service"].unique()) != set(fault["service"].unique()):
            raise ValueError("normal/fault service sets must match")

    def _normalize_types(self, frame: pd.DataFrame) -> None:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
        numeric_columns = [
            "cpu_usage",
            "memory_usage_mb",
            "restart_count",
            "request_rate",
            "error_rate",
            "avg_latency_ms",
            "p50_latency_ms",
            "p90_latency_ms",
            "p95_latency_ms",
            "p99_latency_ms",
            "throughput",
            "http_2xx_rate",
            "http_4xx_rate",
            "http_5xx_rate",
            "network_receive_bytes",
            "network_transmit_bytes",
        ]
        for column in numeric_columns:
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)
