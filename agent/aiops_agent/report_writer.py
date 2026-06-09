from __future__ import annotations

import json
from pathlib import Path

from .models import Diagnosis


class ReportWriter:
    """Write Markdown and JSON reports for AIOps diagnoses."""

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)

    def write(self, diagnoses: list[Diagnosis]) -> tuple[list[str], str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        report_paths = [self._write_markdown(diagnosis) for diagnosis in diagnoses]
        summary_path = self.output_dir / "diagnosis_summary.json"
        payload = {"diagnoses": [diagnosis.to_dict() for diagnosis in diagnoses]}
        summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return [str(path) for path in report_paths], str(summary_path)

    def _write_markdown(self, diagnosis: Diagnosis) -> Path:
        path = self.output_dir / f"diagnosis_{diagnosis.service.replace('-', '_')}_{diagnosis.root_cause}.md"
        lines = [
            "# AIOps Agent 诊断报告",
            "",
            "## 诊断结论",
            "",
            f"检测到 `{diagnosis.service}` 存在 `{diagnosis.root_cause}` 类型异常，严重程度为 `{diagnosis.severity}`。",
            "",
            "## 疑似异常服务",
            "",
            diagnosis.service,
            "",
            "## 根因分类",
            "",
            diagnosis.root_cause,
            "",
            "## 异常证据",
            "",
        ]
        lines.extend(f"- {item}" for item in diagnosis.evidence)
        lines.extend(["", "## 影响范围", ""])
        if diagnosis.affected_services:
            lines.append("可能影响下游服务：" + "、".join(f"`{service}`" for service in diagnosis.affected_services))
        else:
            lines.append("当前规则未识别到明确下游影响服务，建议结合调用链继续确认。")
        lines.extend(["", "## 建议", ""])
        lines.extend(f"- {item}" for item in diagnosis.recommendations)
        lines.extend(["", "## 候选人工确认命令", ""])
        lines.extend(f"```bash\n{command}\n```" for command in diagnosis.candidate_commands)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path
