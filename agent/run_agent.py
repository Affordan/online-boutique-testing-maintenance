#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.aiops_agent.agent import AIOpsAgent


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Online-Boutique AIOps Agent.")
    parser.add_argument(
        "--case",
        default="all",
        choices=["all", "inventory_network_delay", "coupon_cpu_stress", "frontend_pod_kill"],
        help="Diagnosis case to run.",
    )
    parser.add_argument("--normal", default="data/raw/normal_metrics.csv", help="Path to normal metrics CSV.")
    parser.add_argument("--fault", default="data/raw/fault_metrics.csv", help="Path to fault metrics CSV.")
    parser.add_argument("--output-dir", default="results/agent", help="Directory for diagnosis reports.")
    parser.add_argument("--max-reports", type=int, default=3, help="Maximum diagnoses to write.")
    args = parser.parse_args()

    result = AIOpsAgent(args.normal, args.fault, args.output_dir).run(case=args.case, max_reports=args.max_reports)
    print("[AIOps Agent] 诊断完成")
    print(f"报告数量: {len(result.report_paths)}")
    for diagnosis in result.diagnoses:
        print()
        print(f"疑似异常服务: {diagnosis.service}")
        print(f"根因分类: {diagnosis.root_cause}")
        print(f"严重程度: {diagnosis.severity}")
        print("主要证据:")
        for item in diagnosis.evidence[:3]:
            print(f"- {item}")
    print()
    print(f"汇总文件: {result.summary_path}")
    for path in result.report_paths:
        print(f"报告文件: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
