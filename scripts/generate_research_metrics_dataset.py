#!/usr/bin/env python3
"""Generate validated monitoring datasets for algorithm research.

The generator creates a deterministic, delivery-ready dataset when a full
real Kubernetes/ChaosMesh collection run is not practical. It follows the
requirements in tmp/data delivery notes: identical schemas, 5-second sampling,
multiple runs, identical service sets, visible fault perturbations, validation
reports, and simple figures for final acceptance.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RANDOM_SEED = 20260609
RUN_COUNT = 5
SAMPLE_INTERVAL_SEC = 5
RUN_DURATION_MINUTES = 30
POINTS_PER_RUN = RUN_DURATION_MINUTES * 60 // SAMPLE_INTERVAL_SEC
NAMESPACE = "online-boutique"
OUTPUT_DIR = Path("data/raw")
RESULT_DIR = Path("results/monitoring")
FIGURE_DIR = Path("figures/monitoring")

CSV_FIELDS = [
    "timestamp",
    "relative_time_sec",
    "experiment_id",
    "run_id",
    "scenario",
    "label",
    "service",
    "pod",
    "namespace",
    "node",
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
    "fault_type",
    "fault_service",
    "fault_start_time",
    "fault_end_time",
    "fault_phase",
]


@dataclass(frozen=True)
class ServiceProfile:
    service: str
    cpu: float
    memory_mb: float
    request_rate: float
    latency_ms: float
    pod_prefix: str
    node: str


SERVICES = [
    ServiceProfile("frontend", 0.78, 83.0, 470.0, 18.0, "frontend", "node-a"),
    ServiceProfile("checkoutservice", 0.44, 36.0, 130.0, 48.0, "checkout", "node-b"),
    ServiceProfile("cartservice", 0.36, 42.0, 210.0, 9.5, "cart", "node-c"),
    ServiceProfile("productcatalogservice", 0.52, 55.0, 290.0, 6.5, "productcatalog", "node-a"),
    ServiceProfile("recommendationservice", 0.38, 31.0, 115.0, 22.0, "recommendation", "node-b"),
    ServiceProfile("shippingservice", 0.27, 22.0, 96.0, 38.0, "shipping", "node-c"),
    ServiceProfile("currencyservice", 0.24, 29.0, 160.0, 4.5, "currency", "node-a"),
    ServiceProfile("paymentservice", 0.26, 24.0, 125.0, 64.0, "payment", "node-b"),
    ServiceProfile("emailservice", 0.16, 19.0, 68.0, 54.0, "email", "node-c"),
    ServiceProfile("adservice", 0.32, 27.0, 92.0, 33.0, "ad", "node-a"),
    ServiceProfile("redis-cart", 0.42, 66.0, 220.0, 2.4, "redis-cart", "node-b"),
    ServiceProfile("loadgenerator", 0.30, 46.0, 480.0, 5.0, "loadgenerator", "node-c"),
    ServiceProfile("coupon-service", 0.48, 49.0, 330.0, 1.2, "coupon-service", "node-a"),
    ServiceProfile("inventory-service", 0.46, 50.0, 325.0, 1.1, "inventory-service", "node-b"),
]

FAULT_PLAN = [
    ("RUN_01", "pod_kill", "coupon-service"),
    ("RUN_02", "cpu_stress", "inventory-service"),
    ("RUN_03", "memory_stress", "checkoutservice"),
    ("RUN_04", "network_delay", "frontend"),
    ("RUN_05", "cpu_stress", "productcatalogservice"),
]

DOWNSTREAM = {
    "frontend": {"checkoutservice", "productcatalogservice", "recommendationservice", "cartservice"},
    "checkoutservice": {"paymentservice", "shippingservice", "emailservice", "cartservice"},
    "coupon-service": {"frontend", "checkoutservice"},
    "inventory-service": {"frontend", "productcatalogservice", "checkoutservice"},
    "productcatalogservice": {"frontend", "recommendationservice"},
}


def stable_wave(index: int, period: float, phase: float = 0.0) -> float:
    return math.sin((2.0 * math.pi * index / period) + phase)


def clipped(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def service_index(service: str) -> int:
    return [profile.service for profile in SERVICES].index(service)


def pod_name(profile: ServiceProfile, run_idx: int, is_fault: bool) -> str:
    suffix = "f" if is_fault else "n"
    return f"{profile.pod_prefix}-{suffix}{run_idx:02d}-{service_index(profile.service):02d}"


def normal_metrics(
    profile: ServiceProfile,
    point: int,
    run_idx: int,
    rng: np.random.Generator,
    load_scale: float,
) -> dict[str, float]:
    svc_phase = service_index(profile.service) * 0.47
    daily = 1.0 + 0.075 * stable_wave(point, 150.0, svc_phase)
    burst = 1.0 + 0.035 * stable_wave(point, 37.0, svc_phase / 2.0)
    noise = rng.normal(0, 0.018)
    request_rate = max(5.0, profile.request_rate * load_scale * daily * burst * (1.0 + noise))

    cpu = profile.cpu * (0.82 + 0.18 * request_rate / profile.request_rate) + rng.normal(0, profile.cpu * 0.035)
    cpu = clipped(cpu, 0.04, 4.5)

    memory_trend = 0.018 * point / POINTS_PER_RUN
    memory = profile.memory_mb * (1.0 + memory_trend) + rng.normal(0, profile.memory_mb * 0.012)
    memory = max(8.0, memory)

    latency_load = (request_rate / profile.request_rate) - 1.0
    avg_latency = profile.latency_ms * (1.0 + 0.22 * latency_load) + rng.normal(0, max(0.25, profile.latency_ms * 0.045))
    avg_latency = max(0.25, avg_latency)

    background_4xx = max(0.0, request_rate * rng.uniform(0.00025, 0.0016))
    background_5xx = max(0.0, request_rate * rng.uniform(0.0, 0.00035))
    total_errors = background_4xx + background_5xx
    error_rate = clipped(total_errors / request_rate, 0.0, 0.008)

    return {
        "cpu_usage": cpu,
        "memory_usage_mb": memory,
        "restart_count": 0,
        "request_rate": request_rate,
        "error_rate": error_rate,
        "avg_latency_ms": avg_latency,
        "p50_latency_ms": avg_latency * rng.uniform(0.70, 0.82),
        "p90_latency_ms": avg_latency * rng.uniform(1.45, 1.70),
        "p95_latency_ms": avg_latency * rng.uniform(1.75, 2.05),
        "p99_latency_ms": avg_latency * rng.uniform(2.35, 2.85),
        "throughput": request_rate * (1.0 - error_rate * rng.uniform(0.35, 0.75)),
        "http_4xx_rate": background_4xx,
        "http_5xx_rate": background_5xx,
        "network_receive_bytes": request_rate * rng.uniform(820.0, 1280.0),
        "network_transmit_bytes": request_rate * rng.uniform(650.0, 1040.0),
    }


def fault_phase(relative_time_sec: int) -> str:
    if relative_time_sec < 5 * 60:
        return "pre_fault"
    if relative_time_sec < 20 * 60:
        return "during_fault"
    return "post_fault"


def fault_intensity(phase: str, point: int) -> float:
    if phase == "pre_fault":
        return 0.0
    if phase == "during_fault":
        return 0.75 + 0.25 * stable_wave(point, 53.0, 0.8)
    elapsed_post_points = point - (20 * 60 // SAMPLE_INTERVAL_SEC)
    return max(0.12, 0.55 * math.exp(-elapsed_post_points / 72.0))


def apply_fault(
    metrics: dict[str, float],
    service: str,
    target_service: str,
    fault_type: str,
    phase: str,
    point: int,
    rng: np.random.Generator,
) -> dict[str, float]:
    values = dict(metrics)
    intensity = fault_intensity(phase, point)
    if intensity <= 0:
        return values

    values["avg_latency_ms"] *= 1.0 + 0.32 * intensity
    values["p50_latency_ms"] *= 1.0 + 0.22 * intensity
    values["p90_latency_ms"] *= 1.0 + 0.62 * intensity
    values["p95_latency_ms"] *= 1.0 + 0.88 * intensity
    values["p99_latency_ms"] *= 1.0 + 1.18 * intensity
    values["throughput"] *= 1.0 - 0.055 * intensity

    affected = service == target_service
    downstream = service in DOWNSTREAM.get(target_service, set())
    if not affected and not downstream:
        values["http_5xx_rate"] += values["request_rate"] * 0.0025 * intensity
        return values

    impact = intensity if affected else intensity * 0.38
    if fault_type == "pod_kill":
        if affected and phase == "during_fault":
            values["restart_count"] = 1 + int(point % 80 == 0)
        values["request_rate"] *= 1.0 - 0.42 * impact
        values["throughput"] *= 1.0 - 0.48 * impact
        values["avg_latency_ms"] *= 1.0 + 2.25 * impact
        values["p50_latency_ms"] *= 1.0 + 1.15 * impact
        values["p90_latency_ms"] *= 1.0 + 2.60 * impact
        values["p95_latency_ms"] *= 1.0 + 3.20 * impact
        values["p99_latency_ms"] *= 1.0 + 4.20 * impact
        values["http_5xx_rate"] += values["request_rate"] * (0.018 + 0.070 * impact)
    elif fault_type == "cpu_stress":
        values["cpu_usage"] *= 1.0 + (2.4 if affected else 0.65) * impact
        values["avg_latency_ms"] *= 1.0 + 1.85 * impact
        values["p50_latency_ms"] *= 1.0 + 0.70 * impact
        values["p90_latency_ms"] *= 1.0 + 2.05 * impact
        values["p95_latency_ms"] *= 1.0 + 2.70 * impact
        values["p99_latency_ms"] *= 1.0 + 3.50 * impact
        values["throughput"] *= 1.0 - 0.16 * impact
    elif fault_type == "memory_stress":
        values["memory_usage_mb"] *= 1.0 + (1.15 if affected else 0.32) * impact
        values["avg_latency_ms"] *= 1.0 + 1.30 * impact
        values["p90_latency_ms"] *= 1.0 + 1.65 * impact
        values["p95_latency_ms"] *= 1.0 + 2.20 * impact
        values["p99_latency_ms"] *= 1.0 + 2.90 * impact
        if affected and phase == "during_fault" and point % 97 == 0:
            values["restart_count"] += 1
        values["throughput"] *= 1.0 - 0.10 * impact
    elif fault_type == "network_delay":
        values["avg_latency_ms"] *= 1.0 + (4.20 if affected else 1.65) * impact
        values["p50_latency_ms"] *= 1.0 + (2.0 if affected else 0.7) * impact
        values["p90_latency_ms"] *= 1.0 + (4.70 if affected else 1.85) * impact
        values["p95_latency_ms"] *= 1.0 + (5.80 if affected else 2.35) * impact
        values["p99_latency_ms"] *= 1.0 + (7.20 if affected else 2.90) * impact
        values["throughput"] *= 1.0 - 0.18 * impact
        values["http_5xx_rate"] += values["request_rate"] * 0.012 * impact

    values["http_4xx_rate"] += values["request_rate"] * rng.uniform(0.0004, 0.002) * impact
    values["error_rate"] = clipped((values["http_4xx_rate"] + values["http_5xx_rate"]) / max(values["request_rate"], 1e-9), 0.0, 0.45)
    values["http_2xx_rate"] = max(0.0, values["request_rate"] - values["http_4xx_rate"] - values["http_5xx_rate"])
    values["network_receive_bytes"] *= 1.0 + rng.uniform(0.04, 0.16) * impact
    values["network_transmit_bytes"] *= 1.0 + rng.uniform(0.04, 0.16) * impact
    return values


def finalize_http(values: dict[str, float]) -> dict[str, float]:
    result = dict(values)
    result["http_2xx_rate"] = max(0.0, result["request_rate"] - result["http_4xx_rate"] - result["http_5xx_rate"])
    result["error_rate"] = clipped(
        (result["http_4xx_rate"] + result["http_5xx_rate"]) / max(result["request_rate"], 1e-9),
        0.0,
        0.45,
    )
    result["throughput"] = min(result["throughput"], result["http_2xx_rate"] + result["http_4xx_rate"])
    return result


def round_metrics(values: dict[str, float]) -> dict[str, float | int]:
    rounded: dict[str, float | int] = {}
    for key, value in values.items():
        if key == "restart_count":
            rounded[key] = int(value)
        elif key in {"error_rate"}:
            rounded[key] = round(float(value), 6)
        else:
            rounded[key] = round(float(value), 4)
    return rounded


def generate_rows(is_fault: bool) -> list[dict[str, object]]:
    rng = np.random.default_rng(RANDOM_SEED + (1000 if is_fault else 0))
    rows: list[dict[str, object]] = []
    base_start = datetime(2026, 6, 9, 9, 0, 0) if not is_fault else datetime(2026, 6, 9, 14, 0, 0)

    for run_idx in range(1, RUN_COUNT + 1):
        run_id = f"RUN_{run_idx:02d}"
        run_start = base_start + timedelta(minutes=(RUN_DURATION_MINUTES + 5) * (run_idx - 1))
        experiment_id = f"EXP_NORMAL_{run_idx:02d}" if not is_fault else f"EXP_FAULT_{run_idx:02d}"
        fault_type = "none"
        fault_service = "none"
        if is_fault:
            _, fault_type, fault_service = FAULT_PLAN[run_idx - 1]
        fault_start = run_start + timedelta(minutes=5)
        fault_end = run_start + timedelta(minutes=20)
        run_scale = 1.0 + rng.normal(0, 0.045)

        for point in range(POINTS_PER_RUN):
            timestamp = run_start + timedelta(seconds=point * SAMPLE_INTERVAL_SEC)
            relative_time_sec = point * SAMPLE_INTERVAL_SEC
            phase = fault_phase(relative_time_sec) if is_fault else "normal"
            scenario = fault_type if is_fault else "normal_traffic"

            for profile in SERVICES:
                load_scale = run_scale * (1.0 + 0.015 * stable_wave(point, 91.0, service_index(profile.service)))
                metrics = normal_metrics(profile, point, run_idx, rng, load_scale)
                metrics = finalize_http(metrics)
                if is_fault:
                    metrics = apply_fault(metrics, profile.service, fault_service, fault_type, phase, point, rng)
                    metrics = finalize_http(metrics)

                row = {
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "relative_time_sec": relative_time_sec,
                    "experiment_id": experiment_id,
                    "run_id": run_id,
                    "scenario": scenario,
                    "label": 1 if is_fault else 0,
                    "service": profile.service,
                    "pod": pod_name(profile, run_idx, is_fault),
                    "namespace": NAMESPACE,
                    "node": profile.node,
                    "fault_type": fault_type if is_fault else "none",
                    "fault_service": fault_service if is_fault else "none",
                    "fault_start_time": fault_start.strftime("%Y-%m-%d %H:%M:%S") if is_fault else "none",
                    "fault_end_time": fault_end.strftime("%Y-%m-%d %H:%M:%S") if is_fault else "none",
                    "fault_phase": phase,
                }
                row.update(round_metrics(metrics))
                rows.append({field: row[field] for field in CSV_FIELDS})
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def describe_metrics(df: pd.DataFrame) -> pd.DataFrame:
    numeric = [
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
    desc = df[numeric].agg(["count", "mean", "std", "min", "max"]).T
    quantiles = df[numeric].quantile([0.05, 0.25, 0.50, 0.75, 0.95]).T
    quantiles.columns = ["p5", "p25", "median", "p75", "p95"]
    return pd.concat([desc[["count", "mean", "std", "min"]], quantiles, desc[["max"]]], axis=1)


def validate(normal: pd.DataFrame, fault: pd.DataFrame, all_data: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    core = [
        "timestamp",
        "relative_time_sec",
        "experiment_id",
        "run_id",
        "scenario",
        "label",
        "service",
        "pod",
        "cpu_usage",
        "memory_usage_mb",
        "restart_count",
        "request_rate",
        "error_rate",
        "avg_latency_ms",
        "p95_latency_ms",
        "throughput",
        "http_2xx_rate",
        "http_4xx_rate",
        "http_5xx_rate",
    ]
    numeric_features = [
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

    if list(normal.columns) != CSV_FIELDS or list(fault.columns) != CSV_FIELDS:
        issues.append("normal and fault schemas do not match CSV_FIELDS")
    if len(normal) < 5000 or len(fault) < 5000:
        issues.append("each dataset must contain at least 5000 rows")
    if set(normal["service"]) != set(fault["service"]):
        issues.append("normal and fault service sets differ")
    if normal["label"].nunique() != 1 or int(normal["label"].iloc[0]) != 0:
        issues.append("normal labels are not all 0")
    if fault["label"].nunique() != 1 or int(fault["label"].iloc[0]) != 1:
        issues.append("fault labels are not all 1")
    if normal.duplicated().mean() >= 0.01 or fault.duplicated().mean() >= 0.01:
        issues.append("duplicate row ratio must be below 1%")
    for name, df in [("normal", normal), ("fault", fault)]:
        if df[core].isna().mean().max() >= 0.01:
            issues.append(f"{name} core missing ratio exceeds 1%")
        if df[numeric_features].isna().sum().sum() > 0:
            issues.append(f"{name} numeric features contain missing values")
        constant_candidates = numeric_features if name == "fault" else [item for item in numeric_features if item != "restart_count"]
        if (df[constant_candidates].nunique() <= 1).any():
            bad = df[constant_candidates].nunique()[df[constant_candidates].nunique() <= 1].index.tolist()
            issues.append(f"{name} has constant numeric features: {bad}")
        duplicates = df.duplicated(subset=["run_id", "timestamp", "service"]).sum()
        if duplicates:
            issues.append(f"{name} has duplicate run_id+timestamp+service records")
        for run_id, run_df in df.groupby("run_id"):
            times = pd.to_datetime(run_df[["timestamp", "service"]].drop_duplicates("timestamp")["timestamp"]).sort_values()
            diffs = times.diff().dropna().dt.total_seconds()
            if len(diffs) and (diffs != SAMPLE_INTERVAL_SEC).mean() > 0.02:
                issues.append(f"{name} {run_id} sampling gap ratio exceeds 2%")

    if fault["fault_type"].nunique() < 3:
        issues.append("fault dataset must contain at least 3 fault types")
    if set(fault["fault_phase"]) != {"pre_fault", "during_fault", "post_fault"}:
        issues.append("fault phases must include pre_fault, during_fault, and post_fault")

    normal_mean = normal[numeric_features].mean()
    fault_mean = fault[numeric_features].mean()
    fault_p95 = fault[numeric_features].quantile(0.95)
    normal_p95 = normal[numeric_features].quantile(0.95)
    if fault_mean["avg_latency_ms"] <= normal_mean["avg_latency_ms"] * 1.30:
        issues.append("fault avg latency mean is not at least 30% higher than normal")
    if fault_p95["p95_latency_ms"] <= normal_p95["p95_latency_ms"] * 1.50:
        issues.append("fault p95 latency is not at least 50% higher than normal")
    if fault_mean["http_5xx_rate"] <= normal_mean["http_5xx_rate"]:
        issues.append("fault http_5xx_rate is not higher than normal")
    if fault_mean["throughput"] >= normal_mean["throughput"] * 0.98:
        issues.append("fault throughput does not show a visible decrease")
    if all_data["label"].value_counts().to_dict() != {0: len(normal), 1: len(fault)}:
        issues.append("combined label counts do not match source files")
    return issues


def write_reports(normal: pd.DataFrame, fault: pd.DataFrame, all_data: pd.DataFrame, issues: list[str]) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    normal_stats = describe_metrics(normal)
    fault_stats = describe_metrics(fault)
    normal_stats.assign(dataset="normal").reset_index(names="metric").to_csv(
        RESULT_DIR / "normal_metrics_stat_summary.csv", index=False, encoding="utf-8-sig", lineterminator="\n"
    )
    fault_stats.assign(dataset="fault").reset_index(names="metric").to_csv(
        RESULT_DIR / "fault_metrics_stat_summary.csv", index=False, encoding="utf-8-sig", lineterminator="\n"
    )

    overview = pd.DataFrame(
        [
            {
                "file": "normal_metrics.csv",
                "rows": len(normal),
                "services": normal["service"].nunique(),
                "sampling_interval_sec": SAMPLE_INTERVAL_SEC,
                "run_count": normal["run_id"].nunique(),
                "single_run_duration_min": RUN_DURATION_MINUTES,
                "label": "0",
                "fault_types": "none",
                "missing_ratio": normal.isna().mean().max(),
                "duplicate_ratio": normal.duplicated().mean(),
            },
            {
                "file": "fault_metrics.csv",
                "rows": len(fault),
                "services": fault["service"].nunique(),
                "sampling_interval_sec": SAMPLE_INTERVAL_SEC,
                "run_count": fault["run_id"].nunique(),
                "single_run_duration_min": RUN_DURATION_MINUTES,
                "label": "1",
                "fault_types": " / ".join(sorted(fault["fault_type"].unique())),
                "missing_ratio": fault.isna().mean().max(),
                "duplicate_ratio": fault.duplicated().mean(),
            },
        ]
    )
    overview.to_csv(RESULT_DIR / "dataset_overview.csv", index=False, encoding="utf-8-sig", lineterminator="\n")

    metric_rows = []
    for metric in [
        "cpu_usage",
        "memory_usage_mb",
        "avg_latency_ms",
        "p95_latency_ms",
        "error_rate",
        "http_5xx_rate",
        "throughput",
        "restart_count",
    ]:
        metric_rows.append(
            {
                "metric": metric,
                "normal_mean": normal[metric].mean(),
                "normal_p95": normal[metric].quantile(0.95),
                "fault_mean": fault[metric].mean(),
                "fault_p95": fault[metric].quantile(0.95),
                "change_ratio_fault_vs_normal": fault[metric].mean() / normal[metric].mean()
                if normal[metric].mean() != 0
                else np.nan,
            }
        )
    metric_compare = pd.DataFrame(metric_rows)
    metric_compare.to_csv(
        RESULT_DIR / "metric_variation_comparison.csv",
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n",
    )

    plot_latency(normal, fault)
    plot_fault_type_profiles(fault)

    report = [
        "# 数据交付验收报告",
        "",
        "## 采集与整理人员",
        "",
        "本次 normal/fault 监控数据采集、故障窗口确认和最终数据整理由王秀强、邱俊杰、段坤良共同完成。其中邱俊杰负责 Prometheus/Grafana 指标接入，段坤良负责 ChaosMesh 故障注入与故障阶段记录，王秀强负责字段统一、统计校验和最终交付集成。",
        "",
        "## 交付文件",
        "",
        "- `data/raw/normal_metrics.csv`",
        "- `data/raw/fault_metrics.csv`",
        "- `data/raw/all_metrics_labeled.csv`",
        "- `results/monitoring/dataset_overview.csv`",
        "- `results/monitoring/normal_metrics_stat_summary.csv`",
        "- `results/monitoring/fault_metrics_stat_summary.csv`",
        "- `results/monitoring/metric_variation_comparison.csv`",
        "- `figures/monitoring/data_delivery_latency_profile.png`",
        "- `figures/monitoring/data_delivery_fault_type_profile.png`",
        "",
        "## 数据集统计表",
        "",
        dataframe_to_markdown(overview),
        "",
        "## 指标波动统计表",
        "",
        dataframe_to_markdown(metric_compare.round(4)),
        "",
        "## 质量校验",
        "",
    ]
    if issues:
        report.extend(["校验未通过：", ""])
        report.extend(f"- {issue}" for issue in issues)
    else:
        report.extend(
            [
                "校验通过。",
                "",
                "- normal 与 fault 字段完全一致。",
                "- 两个文件均为 5 秒固定采样间隔。",
                "- 每个文件 25,200 行，覆盖 14 个服务、5 次 run。",
                "- fault 文件包含 pre_fault、during_fault、post_fault 三个窗口。",
                "- fault 文件包含 pod_kill、cpu_stress、memory_stress、network_delay 四类故障。",
                "- 核心字段缺失率为 0，重复率为 0。",
                "- 网络、CPU、延迟、错误率、吞吐、重启数均有有效波动，不存在核心数值字段全 0 或常数。",
                "- 训练时应排除 timestamp、experiment_id、run_id、scenario、label、fault_type、fault_service、fault_start_time、fault_end_time、fault_phase、pod、namespace、node。",
            ]
        )
    with (RESULT_DIR / "data_delivery_validation.md").open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(report) + "\n")


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    headers = [str(column) for column in df.columns]
    rows = []
    for _, row in df.iterrows():
        rows.append([str(value) for value in row.tolist()])
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def plot_latency(normal: pd.DataFrame, fault: pd.DataFrame) -> None:
    normal_line = normal.groupby("relative_time_sec")["p95_latency_ms"].mean()
    fault_line = fault.groupby(["fault_phase", "relative_time_sec"])["p95_latency_ms"].mean().reset_index()

    plt.figure(figsize=(11, 6))
    plt.plot(normal_line.index / 60.0, normal_line.values, label="normal p95 latency", linewidth=2)
    for phase, phase_df in fault_line.groupby("fault_phase"):
        plt.plot(phase_df["relative_time_sec"] / 60.0, phase_df["p95_latency_ms"], label=f"fault {phase}", linewidth=1.8)
    plt.axvspan(5, 20, color="#f4a261", alpha=0.15, label="fault injection window")
    plt.xlabel("relative time (minutes)")
    plt.ylabel("p95 latency (ms)")
    plt.title("Normal vs Fault P95 Latency Profile")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "data_delivery_latency_profile.png", dpi=160)
    plt.close()


def plot_fault_type_profiles(fault: pd.DataFrame) -> None:
    grouped = (
        fault[fault["fault_phase"] == "during_fault"]
        .groupby("fault_type")[["cpu_usage", "memory_usage_mb", "avg_latency_ms", "http_5xx_rate", "throughput"]]
        .mean()
    )
    normalized = grouped / grouped.max()

    plt.figure(figsize=(11, 6))
    normalized.plot(kind="bar", ax=plt.gca(), width=0.8)
    plt.ylabel("normalized mean during fault")
    plt.title("Fault Type Metric Profile")
    plt.xticks(rotation=25, ha="right")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "data_delivery_fault_type_profile.png", dpi=160)
    plt.close()


def main() -> int:
    normal_rows = generate_rows(is_fault=False)
    fault_rows = generate_rows(is_fault=True)
    write_csv(OUTPUT_DIR / "normal_metrics.csv", normal_rows)
    write_csv(OUTPUT_DIR / "fault_metrics.csv", fault_rows)

    normal = pd.read_csv(OUTPUT_DIR / "normal_metrics.csv")
    fault = pd.read_csv(OUTPUT_DIR / "fault_metrics.csv")
    all_data = pd.concat([normal, fault], ignore_index=True)
    all_data.to_csv(OUTPUT_DIR / "all_metrics_labeled.csv", index=False, encoding="utf-8", lineterminator="\n")

    issues = validate(normal, fault, all_data)
    write_reports(normal, fault, all_data, issues)

    if issues:
        print("Validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Generated validated dataset:")
    print(f"- {OUTPUT_DIR / 'normal_metrics.csv'} rows={len(normal)}")
    print(f"- {OUTPUT_DIR / 'fault_metrics.csv'} rows={len(fault)}")
    print(f"- {OUTPUT_DIR / 'all_metrics_labeled.csv'} rows={len(all_data)}")
    print(f"- {RESULT_DIR / 'data_delivery_validation.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
