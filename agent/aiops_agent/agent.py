from __future__ import annotations

from pathlib import Path

from .anomaly_detector import AnomalyDetector
from .data_loader import MetricsDataLoader
from .models import AgentResult
from .report_writer import ReportWriter
from .root_cause_classifier import RootCauseClassifier


class AIOpsAgent:
    """Offline AIOps Agent for anomaly detection and diagnosis reports."""

    def __init__(
        self,
        normal_path: str | Path = "data/raw/normal_metrics.csv",
        fault_path: str | Path = "data/raw/fault_metrics.csv",
        output_dir: str | Path = "results/agent",
    ) -> None:
        self.loader = MetricsDataLoader(normal_path, fault_path)
        self.detector = AnomalyDetector()
        self.classifier = RootCauseClassifier()
        self.writer = ReportWriter(output_dir)

    def run(self, case: str = "all", max_reports: int = 3) -> AgentResult:
        normal, fault = self.loader.load()
        anomalies = self.detector.detect(normal, fault, case=case)
        diagnoses = [self.classifier.classify(anomaly, normal, fault) for anomaly in anomalies[:max_reports]]
        report_paths, summary_path = self.writer.write(diagnoses)
        return AgentResult(diagnoses=diagnoses, summary_path=summary_path, report_paths=report_paths)
