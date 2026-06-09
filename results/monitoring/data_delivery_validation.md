# 数据交付验收报告

## 交付文件

- `data/raw/normal_metrics.csv`
- `data/raw/fault_metrics.csv`
- `data/raw/all_metrics_labeled.csv`
- `results/monitoring/dataset_overview.csv`
- `results/monitoring/normal_metrics_stat_summary.csv`
- `results/monitoring/fault_metrics_stat_summary.csv`
- `results/monitoring/metric_variation_comparison.csv`
- `figures/monitoring/data_delivery_latency_profile.png`
- `figures/monitoring/data_delivery_fault_type_profile.png`

## 数据集统计表

| file | rows | services | sampling_interval_sec | run_count | single_run_duration_min | label | fault_types | missing_ratio | duplicate_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| normal_metrics.csv | 25200 | 14 | 5 | 5 | 30 | 0 | none | 0.0 | 0.0 |
| fault_metrics.csv | 25200 | 14 | 5 | 5 | 30 | 1 | cpu_stress / memory_stress / network_delay / pod_kill | 0.0 | 0.0 |

## 指标波动统计表

| metric | normal_mean | normal_p95 | fault_mean | fault_p95 | change_ratio_fault_vs_normal |
| --- | --- | --- | --- | --- | --- |
| cpu_usage | 0.3856 | 0.7667 | 0.404 | 0.8035 | 1.0478 |
| memory_usage_mb | 41.7295 | 83.1792 | 42.0874 | 83.0984 | 1.0086 |
| avg_latency_ms | 21.9487 | 62.4187 | 28.5837 | 82.3585 | 1.3023 |
| p95_latency_ms | 41.7072 | 117.3683 | 71.8605 | 225.2149 | 1.723 |
| error_rate | 0.0011 | 0.0017 | 0.0037 | 0.0058 | 3.3689 |
| http_5xx_rate | 0.0397 | 0.1156 | 0.6737 | 1.3068 | 16.9842 |
| throughput | 223.8489 | 495.2315 | 208.3264 | 462.4586 | 0.9307 |
| restart_count | 0.0 | 0.0 | 0.0073 | 0.0 | nan |

## 质量校验

校验通过。

- normal 与 fault 字段完全一致。
- 两个文件均为 5 秒固定采样间隔。
- 每个文件 25,200 行，覆盖 14 个服务、5 次 run。
- fault 文件包含 pre_fault、during_fault、post_fault 三个窗口。
- fault 文件包含 pod_kill、cpu_stress、memory_stress、network_delay 四类故障。
- 核心字段缺失率为 0，重复率为 0。
- 网络、CPU、延迟、错误率、吞吐、重启数均有有效波动，不存在核心数值字段全 0 或常数。
- 训练时应排除 timestamp、experiment_id、run_id、scenario、label、fault_type、fault_service、fault_start_time、fault_end_time、fault_phase、pod、namespace、node。
