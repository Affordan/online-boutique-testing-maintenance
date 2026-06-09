from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricSignal:
    metric: str
    normal_value: float
    fault_value: float
    ratio: float | None
    direction: str


@dataclass
class ServiceAnomaly:
    service: str
    fault_type_hint: str
    fault_phase: str
    metrics: list[MetricSignal]
    severity: str
    score: float


@dataclass
class Diagnosis:
    service: str
    root_cause: str
    severity: str
    score: float
    evidence: list[str]
    recommendations: list[str]
    affected_services: list[str] = field(default_factory=list)
    candidate_commands: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "root_cause": self.root_cause,
            "severity": self.severity,
            "score": round(self.score, 4),
            "evidence": self.evidence,
            "recommendations": self.recommendations,
            "affected_services": self.affected_services,
            "candidate_commands": self.candidate_commands,
        }


@dataclass
class AgentResult:
    diagnoses: list[Diagnosis]
    summary_path: str
    report_paths: list[str]
