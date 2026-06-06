# ChaosMesh 故障注入实验记录

本文记录 Online-Boutique 微服务系统中使用 ChaosMesh 进行的故障注入实验。

## 1. 目标

使用 ChaosMesh 对系统进行故障注入实验，验证系统在以下故障场景下的行为：

1. **Pod Kill** — 杀死目标服务 Pod，验证 Kubernetes 自动恢复能力。
2. **CPU Stress** — 对目标服务注入 CPU 压力，观察性能影响。
3. **Network Delay** — 对目标服务注入网络延迟，验证服务间调用的容错性。

## 2. 前置条件

部署 ChaosMesh 前先确认：

`ash
bash scripts/check_env.sh
bash scripts/start_minikube.sh
bash scripts/deploy_online_boutique.sh
kubectl get pods -n online-boutique
`

确认所有服务 Pod 处于 Running 状态。

## 3. 安装 ChaosMesh

使用 Helm 安装 ChaosMesh：

`ash
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update
kubectl create ns chaos-mesh
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh --version 2.7.0
`

验证 ChaosMesh 组件运行状态：

`ash
kubectl get pods -n chaos-mesh
`

## 4. 实验设计

共设计 6 个故障注入实验，覆盖 3 种故障类型 x 2 个目标服务：

| 实验编号 | 故障类型 | 目标服务 | 配置文件 |
|---------|---------|---------|---------|
| F001 | Pod Kill | coupon-service | chaos/chaos_pod_kill_coupon.yaml |
| F002 | Pod Kill | inventory-service | chaos/chaos_pod_kill_inventory.yaml |
| F003 | CPU Stress | coupon-service | chaos/chaos_cpu_stress_coupon.yaml |
| F004 | Network Delay | inventory-service | chaos/chaos_network_delay_inventory.yaml |
| F005 | Network Delay | coupon-service | chaos/chaos_network_delay_coupon.yaml |
| F006 | CPU Stress | inventory-service | chaos/chaos_cpu_stress_inventory.yaml |

## 5. 实验执行步骤

### 5.1 通用步骤

每个实验按以下步骤执行：

1. 应用实验配置：\kubectl apply -f chaos/<config-file>.yaml\
2. 验证实验状态：\kubectl get <chaos-type> -n chaos-mesh\
3. 查看实验详情：\kubectl describe <chaos-type> <experiment-name> -n chaos-mesh\
4. 确认注入成功（AllInjected: True）
5. 清理实验：\kubectl delete <chaos-type> <experiment-name> -n chaos-mesh\

### 5.2 注意事项

- 当前 ChaosMesh 版本的 PodChaos、StressChaos、NetworkChaos 均不支持 spec.scheduler 字段，需从 YAML 中移除。
- NetworkChaos 的 correlation 字段需使用字符串类型（如 \"50"\）而非数字类型。
- 实验注入成功后无需等待完整 duration，可随时手动清理。

## 6. 实验结果

实验结果详情见 \esults/chaos/experiment_results.md\，截图见 \igures/chaos/\。

## 7. 截图清单

| 文件 | 说明 |
|------|------|
| screenshot_01_all_pods_running.png | 初始状态 - 所有 Pod 运行中 |
| screenshot_02_chaosmesh_pods.png | ChaosMesh 组件 Pod |
| screenshot_03_f001_yaml.png | F001 YAML 配置内容 |
| screenshot_04_f001_applied.png | F001 创建成功 |
| screenshot_05_f001_describe.png | F001 实验详情 |
| screenshot_06_f002_describe.png | F002 实验详情 |
| screenshot_07_f002_recovered.png | F002 恢复状态 |
| screenshot_08_f002_deleted.png | F002 清理完成 |
| screenshot_09_f003_applied.png | F003 创建成功 |
| screenshot_10_f003_describe.png | F003 实验详情 |
| screenshot_11_f003_deleted.png | F003 清理完成 |
| screenshot_12_f004_applied.png | F004 创建成功 |
| screenshot_13_f004_describe.png | F004 实验详情 |
| screenshot_14_f004_deleted.png | F004 清理完成 |
| screenshot_15_f005_applied.png | F005 创建成功 |
| screenshot_16_f005_describe.png | F005 实验详情 |
| screenshot_17_f005_deleted.png | F005 清理完成 |
| screenshot_18_f006_applied.png | F006 创建成功 |
| screenshot_19_f006_describe.png | F006 实验详情 |
| screenshot_20_f006_deleted.png | F006 清理完成 |
