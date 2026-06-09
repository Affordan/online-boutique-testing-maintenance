import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from agent.aiops_agent.agent import AIOpsAgent
from agent.aiops_agent.anomaly_detector import AnomalyDetector
from agent.aiops_agent.data_loader import MetricsDataLoader
from agent.aiops_agent.root_cause_classifier import RootCauseClassifier


FIELDS = [
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


def make_row(service, label, fault_type="none", fault_phase="normal", **overrides):
    base = {
        "timestamp": "2026-06-09 09:00:00",
        "relative_time_sec": 0,
        "experiment_id": "EXP_TEST",
        "run_id": "RUN_01",
        "scenario": "normal_traffic" if label == 0 else fault_type,
        "label": label,
        "service": service,
        "pod": f"{service}-pod",
        "namespace": "online-boutique",
        "node": "node-a",
        "cpu_usage": 0.3,
        "memory_usage_mb": 50.0,
        "restart_count": 0,
        "request_rate": 100.0,
        "error_rate": 0.001,
        "avg_latency_ms": 10.0,
        "p50_latency_ms": 8.0,
        "p90_latency_ms": 16.0,
        "p95_latency_ms": 20.0,
        "p99_latency_ms": 28.0,
        "throughput": 99.0,
        "http_2xx_rate": 99.0,
        "http_4xx_rate": 0.09,
        "http_5xx_rate": 0.01,
        "network_receive_bytes": 100000.0,
        "network_transmit_bytes": 80000.0,
        "fault_type": fault_type,
        "fault_service": service if label == 1 else "none",
        "fault_start_time": "none",
        "fault_end_time": "none",
        "fault_phase": fault_phase,
    }
    base.update(overrides)
    return base


class AIOpsAgentTest(unittest.TestCase):
    def test_loader_requires_matching_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            normal_path = Path(tmp) / "normal.csv"
            fault_path = Path(tmp) / "fault.csv"
            pd.DataFrame([make_row("frontend", 0)])[FIELDS].to_csv(normal_path, index=False)
            pd.DataFrame([make_row("frontend", 1, fault_type="network_delay", fault_phase="during_fault")])[
                FIELDS[:-1]
            ].to_csv(fault_path, index=False)

            loader = MetricsDataLoader(normal_path, fault_path)

            with self.assertRaisesRegex(ValueError, "schema"):
                loader.load()

    def test_detector_finds_service_metric_anomalies(self):
        normal = pd.DataFrame(
            [
                make_row("inventory-service", 0, p95_latency_ms=20, p99_latency_ms=30, error_rate=0.001),
                make_row("inventory-service", 0, p95_latency_ms=22, p99_latency_ms=33, error_rate=0.0012),
            ]
        )
        fault = pd.DataFrame(
            [
                make_row(
                    "inventory-service",
                    1,
                    fault_type="network_delay",
                    fault_phase="during_fault",
                    p95_latency_ms=110,
                    p99_latency_ms=180,
                    error_rate=0.01,
                    throughput=70,
                )
            ]
        )

        anomalies = AnomalyDetector().detect(normal, fault)

        self.assertEqual(anomalies[0].service, "inventory-service")
        self.assertIn("p95_latency_ms", {signal.metric for signal in anomalies[0].metrics})
        self.assertEqual(anomalies[0].severity, "high")

    def test_classifier_prioritizes_pod_kill_when_restart_increases(self):
        normal = pd.DataFrame([make_row("frontend", 0, restart_count=0, http_5xx_rate=0.01)])
        fault = pd.DataFrame(
            [
                make_row(
                    "frontend",
                    1,
                    fault_type="pod_kill",
                    fault_phase="during_fault",
                    restart_count=2,
                    http_5xx_rate=5.0,
                    error_rate=0.08,
                )
            ]
        )
        anomaly = AnomalyDetector().detect(normal, fault)[0]

        diagnosis = RootCauseClassifier().classify(anomaly, normal, fault)

        self.assertEqual(diagnosis.root_cause, "pod_kill")
        self.assertIn("restart_count", " ".join(diagnosis.evidence))
        self.assertTrue(diagnosis.recommendations)

    def test_agent_writes_markdown_report_and_summary_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            normal_path = tmp_path / "normal.csv"
            fault_path = tmp_path / "fault.csv"
            output_dir = tmp_path / "results"
            pd.DataFrame([make_row("frontend", 0)])[FIELDS].to_csv(normal_path, index=False)
            pd.DataFrame(
                [
                    make_row(
                        "frontend",
                        1,
                        fault_type="pod_kill",
                        fault_phase="during_fault",
                        restart_count=2,
                        http_5xx_rate=4.5,
                        error_rate=0.05,
                        throughput=60,
                    )
                ]
            )[FIELDS].to_csv(fault_path, index=False)

            result = AIOpsAgent(normal_path=normal_path, fault_path=fault_path, output_dir=output_dir).run(case="all")

            self.assertEqual(result.diagnoses[0].root_cause, "pod_kill")
            report_path = output_dir / "diagnosis_frontend_pod_kill.md"
            summary_path = output_dir / "diagnosis_summary.json"
            self.assertTrue(report_path.exists())
            self.assertTrue(summary_path.exists())
            self.assertIn("AIOps Agent 诊断报告", report_path.read_text(encoding="utf-8"))
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["diagnoses"][0]["root_cause"], "pod_kill")


if __name__ == "__main__":
    unittest.main()
