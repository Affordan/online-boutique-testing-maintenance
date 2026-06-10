#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KPIRoot: Efficient Monitoring Metric-based Root Cause Localization
Full implementation based on ISSRE 2024 paper.

Supports:
- SAX symbolic representation with dynamic alphabet size
- Anomaly segment detection (with fallback to whole window)
- n-gram Jaccard similarity on SAX sequences
- Granger causality with p-value filtering (p < 0.05)
- Multi-feature weighted fusion
- Automatic alarm KPI selection
- Evaluation metrics (Hit@K, F1-score) if ground truth provided
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
import warnings
warnings.filterwarnings("ignore")

# ====================== 配置参数（可根据需要修改） ======================
plt.rcParams['font.sans-serif'] = ['SimHei']      # 中文显示（Windows）
plt.rcParams['axes.unicode_minus'] = False

# SAX 参数
W = 20                        # SAX 降维后目标长度
ALPHABET_SIZE_MAX = 9         # 最大符号集大小
N_GRAM_DEFAULT = 3            # n-gram 长度（用于 Jaccard）

# 异常检测参数
GAMMA = 1.5                   # 尖峰检测阈值
L = 5                         # 趋势检测窗口宽度

# 融合参数
LAMBDA = 0.9                  # 相似度权重，因果权重 = 1 - LAMBDA

# Granger 因果参数
MAX_LAG = 3                   # 最大滞后阶数
CAUSAL_P_THRESHOLD = 0.05     # 因果检验显著性阈值

# 多特征权重（若 multi_feature=True 则使用）
FEATURE_WEIGHTS = {
    'request_rate': 1.0,
    'error_rate': 1.5,
    'avg_latency_ms': 1.2,
    'cpu_usage': 1.0,
    'memory_usage_mb': 0.8,
    'restart_count': 3.0
}

# 是否使用多特征融合（False 则只使用 request_rate 或 error_rate）
MULTI_FEATURE = True

# ====================== 基础时序变换函数 ======================
def paa_transform(series, w):
    """Piecewise Aggregate Approximation"""
    series = np.asarray(series, dtype=float)
    n = len(series)
    if n <= w:
        return series
    indices = np.linspace(0, n, w + 1, dtype=int)
    return np.array([np.mean(series[indices[i]:indices[i+1]]) for i in range(w)])

def sax_transform(series, w, alpha):
    """SAX 符号化表示，返回整数编码序列"""
    series = np.asarray(series, dtype=float)
    mean_val = np.mean(series)
    std_val = np.std(series)
    if std_val < 1e-8:
        normalized = series - mean_val
    else:
        normalized = (series - mean_val) / std_val
    paa_seq = paa_transform(normalized, w)
    breakpoints = norm.ppf(np.linspace(0, 1, alpha + 1)[1:-1])
    symbols = np.digitize(paa_seq, breakpoints)
    return symbols

# ====================== 异常窗口检测 ======================
def detect_anomaly_window(series, l=L, gamma=GAMMA):
    """
    检测尖峰型异常区间，若无尖峰则返回整个序列区间 [0, n-1]
    """
    series = np.asarray(series, dtype=float)
    n = len(series)
    if n < 2 * l + 2:
        return 0, n - 1

    scores = []
    for i in range(l, n - l):
        forward = np.sum(series[i:i+l])
        backward = np.sum(series[i-l:i+l])
        ratio = forward / (backward + 1e-8)
        scores.append(ratio)
    scores = np.array(scores)

    if np.max(scores) > gamma:
        pos_arr = np.where(scores > gamma)[0]
        start_offset = pos_arr[0]
        ts = start_offset + l
        te = ts
        # 回落条件：当前点值仍高于异常起始点
        while te + 1 < n and series[te+1] > series[ts]:
            te += 1
        return ts, te
    return 0, n - 1

# ====================== Jaccard 相似度（支持 n-gram） ======================
def jaccard_similarity_basic(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

def jaccard_ngram_similarity(sax1, sax2, n=N_GRAM_DEFAULT):
    """基于 n-gram 的 Jaccard 相似度，保留时序局部顺序"""
    sax1 = np.asarray(sax1)
    sax2 = np.asarray(sax2)
    len1, len2 = len(sax1), len(sax2)
    if len1 < n or len2 < n or n < 2:
        # 序列过短，退化为普通集合 Jaccard
        return jaccard_similarity_basic(set(sax1), set(sax2))
    set1 = set(tuple(sax1[i:i+n]) for i in range(len1 - n + 1))
    set2 = set(tuple(sax2[i:i+n]) for i in range(len2 - n + 1))
    return jaccard_similarity_basic(set1, set2)

# ====================== Granger 因果检验（带显著性过滤） ======================
def make_stationary(seq, max_diff=2):
    """通过差分使序列平稳（ADF检验）"""
    seq = np.asarray(seq, dtype=float)
    diff_seq = seq
    for _ in range(max_diff):
        if len(diff_seq) < 4:
            break
        try:
            p_val = adfuller(diff_seq, autolag='AIC')[1]
        except Exception:
            p_val = 0.5
        if p_val < 0.05:
            return diff_seq
        diff_seq = np.diff(diff_seq)
    return diff_seq

def granger_causality_score(cause_seq, effect_seq, maxlag=MAX_LAG, p_thresh=CAUSAL_P_THRESHOLD):
    """
    计算 cause_seq -> effect_seq 的 Granger 因果强度。
    返回显著滞后阶数的平均 F-statistic，若无显著阶数则返回 0。
    """
    if len(cause_seq) < maxlag + 4 or len(effect_seq) < maxlag + 4:
        return 0.0
    if np.std(cause_seq) < 1e-8 or np.std(effect_seq) < 1e-8:
        return 0.0

    x_st = make_stationary(cause_seq)   # cause
    y_st = make_stationary(effect_seq)  # effect
    min_len = min(len(x_st), len(y_st))
    if min_len < maxlag + 4:
        return 0.0
    x_st = x_st[-min_len:]
    y_st = y_st[-min_len:]
    # 数据格式：第一列 = 被解释变量(effect)，第二列 = 解释变量(cause)
    data = np.column_stack([y_st, x_st])

    try:
        res = grangercausalitytests(data, maxlag=maxlag, verbose=False)
        f_vals = []
        for lag in range(1, maxlag+1):
            f_stat, p_val = res[lag][0]['ssr_ftest'][0], res[lag][0]['ssr_ftest'][1]
            if p_val < p_thresh:
                f_vals.append(f_stat)
        return float(np.mean(f_vals)) if f_vals else 0.0
    except Exception:
        return 0.0

# ====================== KPIRoot 核心评分 ======================
def kpi_root_core(vm_series, alarm_series, ts, te, debug=False):
    """
    对单个 VM 的某个 KPI 计算与 Alarm KPI 之间的根因得分。
    vm_series, alarm_series: 对齐的完整时序
    ts, te: 异常窗口（已预先计算）
    返回 (similarity, causality, total_score)
    """
    if te - ts + 1 < 3:
        if debug:
            print("    异常窗口长度不足，跳过")
        return 0.0, 0.0, 0.0

    alarm_seg = alarm_series[ts:te+1]
    vm_seg = vm_series[ts:te+1]
    seg_len = len(alarm_seg)
    if seg_len < 3:
        return 0.0, 0.0, 0.0

    # 动态 SAX 参数
    w_actual = min(W, seg_len)
    alpha_actual = min(ALPHABET_SIZE_MAX, max(2, seg_len // 2))
    alarm_sax = sax_transform(alarm_seg, w_actual, alpha_actual)
    vm_sax = sax_transform(vm_seg, w_actual, alpha_actual)

    # n-gram Jaccard（动态 n）
    n_gram = min(N_GRAM_DEFAULT, seg_len // 2)
    similarity = jaccard_ngram_similarity(vm_sax, alarm_sax, n=n_gram)

    # Granger causality — 注意：传入的是异常段数据！
    causality = granger_causality_score(vm_seg, alarm_seg)   # 修正：原为 alarm_series，现为 alarm_seg

    total_score = LAMBDA * similarity + (1 - LAMBDA) * causality

    if debug:
        print(f"    窗口[{ts},{te}] | 相似度:{similarity:.3f} 因果分:{causality:.3f} 综合分:{total_score:.3f}")
    return similarity, causality, total_score

# ====================== 自动选择报警 KPI ======================
def select_alarm_kpi(pre_df, during_df):
    """
    根据故障阶段数据自动选择最敏感的指标作为 Alarm KPI。
    优先选择有重启计数的指标；否则选择故障前后变化率最大的指标。
    """
    # 优先使用重启计数
    if 'restart_count' in during_df.columns:
        restart_agg = during_df.groupby('timestamp')['restart_count'].sum()
        if restart_agg.max() > 0:
            return 'restart_count', restart_agg.values

    candidates = ['error_rate', 'avg_latency_ms', 'request_rate', 'cpu_usage']
    best_col = 'error_rate'
    max_ratio = -1.0
    for col in candidates:
        if col not in during_df.columns:
            continue
        pre_mean = pre_df[col].mean() if not pre_df.empty else 0.0
        during_mean = during_df[col].mean()
        if pre_mean < 1e-8:
            ratio = during_mean + 1.0
        else:
            ratio = during_mean / pre_mean
        if ratio > max_ratio:
            max_ratio = ratio
            best_col = col
    alarm_agg = during_df.groupby('timestamp')[best_col].mean()
    return best_col, alarm_agg.values

# ====================== 评估指标计算（可选） ======================
def evaluate_hit_k(pred_services, true_root_cause, k_list=[1,3,5,10]):
    """
    计算 Hit@K 指标
    pred_services: 按得分降序排列的服务列表
    true_root_cause: 真实根因服务名称（字符串）或列表
    """
    if isinstance(true_root_cause, str):
        true_set = {true_root_cause}
    else:
        true_set = set(true_root_cause)
    results = {}
    for k in k_list:
        hit = len(set(pred_services[:k]) & true_set) > 0
        results[f"Hit@{k}"] = hit
    return results

def evaluate_f1(pred_services, true_root_cause_set, top_k=None):
    """
    计算 F1-score（若预测 top_k 个，取前 top_k）
    若 top_k 为 None，则将所有预测服务视为正例
    """
    if top_k is not None:
        pred_set = set(pred_services[:top_k])
    else:
        pred_set = set(pred_services)
    true_set = set(true_root_cause_set) if isinstance(true_root_cause_set, (list, tuple)) else {true_root_cause_set}
    intersection = len(pred_set & true_set)
    if intersection == 0:
        return 0.0
    precision = intersection / len(pred_set)
    recall = intersection / len(true_set)
    return 2 * precision * recall / (precision + recall)

# ====================== 单实验处理主逻辑 ======================
def process_experiment(exp_id, exp_df, fault_type, true_root_cause=None, multi_feature=MULTI_FEATURE):
    """
    exp_df: 包含实验数据，至少包含列：timestamp, service, fault_phase, 及各指标列
    true_root_cause: 可选，真实根因服务名称（用于评估）
    """
    pre_df = exp_df[exp_df['fault_phase'] == 'pre_fault']
    during_df = exp_df[exp_df['fault_phase'] == 'during_fault'].copy()
    if pre_df.empty or during_df.empty:
        print(f"[警告] 实验 {exp_id} 缺失故障阶段数据，跳过")
        return None

    services = during_df['service'].unique()
    time_index = sorted(during_df['timestamp'].unique())

    # 获取报警序列
    alarm_name, alarm_raw = select_alarm_kpi(pre_df, during_df)
    alarm_series = during_df.groupby('timestamp')[alarm_name].mean()
    alarm_series = alarm_series.reindex(time_index).fillna(0.0).values

    # 全局异常窗口
    ts, te = detect_anomaly_window(alarm_series)
    print(f"  异常窗口: [{ts}, {te}] (长度 {te-ts+1})")

    # 选择参与的特征
    if multi_feature:
        features = [f for f in FEATURE_WEIGHTS.keys() if f in during_df.columns]
    else:
        features = ['request_rate'] if 'request_rate' in during_df.columns else ['cpu_usage']

    if not features:
        print(f"[警告] 实验 {exp_id} 无有效分析特征，跳过")
        return None

    # 存储每个特征的所有服务原始得分
    feature_raw_scores = {feat: {} for feat in features}
    print(f"\n===== 实验 {exp_id} | 故障类型:{fault_type} | 报警KPI:{alarm_name} =====")
    print(f"参与特征: {features}")

    for feat in features:
        weight = FEATURE_WEIGHTS.get(feat, 1.0)
        print(f"\n>> 特征 {feat} (权重={weight})")
        # 构建服务×时间的透视表
        pivot = during_df.pivot_table(
            index='timestamp', columns='service', values=feat, aggfunc='mean'
        ).reindex(time_index)
        pivot = pivot.interpolate(limit_direction='both').fillna(0.0)

        for svc in services:
            svc_series = pivot[svc].values
            _, _, score = kpi_root_core(svc_series, alarm_series, ts, te, debug=(svc == services[0]))
            feature_raw_scores[feat][svc] = score

    # 分层归一化 + 加权累加
    service_total_score = {svc: 0.0 for svc in services}
    for feat in features:
        weight = FEATURE_WEIGHTS.get(feat, 1.0)
        scores = list(feature_raw_scores[feat].values())
        min_s, max_s = min(scores), max(scores)
        if max_s - min_s < 1e-8:
            norm_scores = {svc: 0.0 for svc in services}
        else:
            norm_scores = {svc: (feature_raw_scores[feat][svc] - min_s) / (max_s - min_s) for svc in services}
        for svc in services:
            service_total_score[svc] += weight * norm_scores[svc]

    # 最终归一化到 [0,1]
    all_scores = list(service_total_score.values())
    max_s = max(all_scores) if all_scores else 1.0
    if max_s > 1e-8:
        for svc in service_total_score:
            service_total_score[svc] /= max_s

    # 排序
    sorted_svc = sorted(service_total_score.items(), key=lambda x: x[1], reverse=True)

    # 输出排名
    print("\n【根因服务排名】")
    for idx, (name, sc) in enumerate(sorted_svc[:10], 1):
        print(f"  {idx:2d}. {name:<30s} 得分: {sc:.4f}")

    # 可视化并保存图片（仅保留图像输出）
    plt.figure(figsize=(10, 6))
    top_n = min(15, len(sorted_svc))
    names = [item[0] for item in sorted_svc[:top_n]]
    scores = [item[1] for item in sorted_svc[:top_n]]
    plt.barh(names, scores, color='#4472C4')
    plt.xlabel("归一化异常得分")
    plt.title(f"KPIRoot 根因排名 | {exp_id} ({fault_type})")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f"KPIRoot_result_{exp_id}.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  可视化图已保存: KPIRoot_result_{exp_id}.png")

    # 评估（如果提供了真实根因，仅控制台打印，不导出CSV）
    if true_root_cause is not None:
        pred_services = [svc for svc, _ in sorted_svc]
        hit_metrics = evaluate_hit_k(pred_services, true_root_cause, k_list=[1,3,5,10])
        f1_at_5 = evaluate_f1(pred_services, true_root_cause, top_k=5)
        print("\n【评估结果】")
        for k, v in hit_metrics.items():
            print(f"  {k}: {v}")
        print(f"  F1@5: {f1_at_5:.4f}")

    return sorted_svc

# ====================== 主程序 ======================
def main():
    try:
        df = pd.read_csv("fault_metrics.csv", encoding="utf-8-sig")
    except FileNotFoundError:
        print("错误：未找到 fault_metrics.csv 文件，请将数据文件放在代码同目录！")
        return

    # 确保时间戳列存在并排序
    if 'timestamp' not in df.columns:
        print("错误：数据文件缺少 timestamp 列")
        return
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['experiment_id', 'timestamp', 'service']).reset_index(drop=True)

    exp_list = df['experiment_id'].unique()
    print(f"共检测到 {len(exp_list)} 组实验: {list(exp_list)}")

    for exp_id in exp_list:
        exp_df = df[df['experiment_id'] == exp_id].copy()
        fault_type = exp_df['fault_type'].iloc[0] if 'fault_type' in exp_df.columns else "未知故障"
        # 提取真值（仅用于控制台评估，不生成文件）
        true_rc = None
        if 'root_cause_service' in exp_df.columns:
            true_vals = exp_df['root_cause_service'].dropna().unique()
            if len(true_vals) > 0:
                true_rc = true_vals[0]
        process_experiment(exp_id, exp_df, fault_type, true_root_cause=true_rc, multi_feature=MULTI_FEATURE)

    print("\n========== 全部实验分析完成 ==========")

if __name__ == "__main__":
    main()