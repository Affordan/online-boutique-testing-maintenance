#!/usr/bin/env python3
import argparse
import csv
import sys
import time
from pathlib import Path

from export_monitoring_metrics import CSV_FIELDS, build_rows


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return parsed


def non_negative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be greater than or equal to 0")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Continuously record Online-Boutique monitoring metrics from Prometheus until enough CSV rows are collected."
    )
    parser.add_argument("--prometheus-url", default="http://localhost:9090")
    parser.add_argument("--experiment-id", default="EXP_10000")
    parser.add_argument("--scenario", default="experiment_traffic")
    parser.add_argument("--output", default="data/raw/monitoring_metrics_10000.csv")
    parser.add_argument("--target-rows", type=positive_int, default=10000)
    parser.add_argument(
        "--interval-seconds",
        type=non_negative_float,
        default=1.0,
        help="Delay between Prometheus samples. Use >=15 for independent scrape windows; smaller values finish faster.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append rows to an existing CSV instead of replacing it.",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    mode = "a" if args.append and output.exists() else "w"
    rows_written = 0
    sample_count = 0

    with output.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        if mode == "w":
            writer.writeheader()

        while rows_written < args.target_rows:
            sample_count += 1
            rows = build_rows(args.prometheus_url, args.experiment_id, args.scenario)
            if not rows:
                print(
                    "No rows returned from Prometheus. Check Prometheus port-forward, Targets UP, and service traffic.",
                    file=sys.stderr,
                )
                return 1

            remaining = args.target_rows - rows_written
            rows_to_write = rows[:remaining]
            writer.writerows(rows_to_write)
            handle.flush()
            rows_written += len(rows_to_write)

            print(f"sample={sample_count} wrote={rows_written}/{args.target_rows} rows", flush=True)

            if rows_written < args.target_rows and args.interval_seconds > 0:
                time.sleep(args.interval_seconds)

    print(f"Wrote {rows_written} rows to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
