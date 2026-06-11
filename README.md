# Online-Boutique 微服务测试与维护大作业

本仓库用于《软件测试与维护》课程大作业。项目选择 **Online-Boutique** 作为实验对象，围绕微服务系统完成本地部署、监控、故障注入、自动化测试、性能测试、异常数据采集、论文算法复现，并在原系统基础上新增业务微服务。

Online-Boutique 是一个在线商店系统，包含前端、商品目录、购物车、结算、支付、推荐、邮件、广告、负载生成等服务。它的业务关系清楚，服务数量适中，适合观察微服务之间的调用、运行状态变化和故障传播现象。

本项目采用本地 Kubernetes 环境部署，主要使用 Docker、Minikube、kubectl 和 Helm 完成系统运行与管理。当前项目暂不使用 Google Cloud。本地环境已经能够满足课程实验需求，同时可以避免云平台账号、计费、权限和网络访问带来的额外成本。

当前已完成：

- Online-Boutique 主系统已在本地 Minikube 集群中成功部署。
- 新增 `coupon-service` 优惠券微服务。
- 新增 `inventory-service` 库存微服务。
- 两个新增服务已完成容器构建、Minikube 镜像导入、Kubernetes 部署和接口验证。
- `frontend`、`checkoutservice`、`productcatalogservice` 已通过环境变量接入新增服务地址。
- 已按数据交付要求重新整理 `normal_metrics.csv`、`fault_metrics.csv` 和 `all_metrics_labeled.csv`，并生成统计验收报告与可视化图。
- 论文算法复现已完成，当前保留 DA-VAE 异常检测、KPIRoot 根因定位代码、论文材料、输出图和结论说明。
- 报告 PDF 与展示 PPT 已预留独立目录，后续可直接基于 README、截图和实验结果整理成稿。

---

## 1. 项目目标

本项目围绕 Online-Boutique 完成以下工作：

1. 在本地 Kubernetes 环境中部署 Online-Boutique 微服务系统。
2. 梳理系统服务组成、服务职责和核心业务请求。
3. 新增两个业务微服务：`coupon-service` 和 `inventory-service`。
4. 接入 Prometheus 和 Grafana，采集并展示系统运行指标。
5. 使用 ChaosMesh 对系统进行故障注入实验。
6. 使用 Selenium 进行功能自动化测试。
7. 使用 JMeter 进行并发性能测试。
8. 从 Prometheus 导出正常状态和故障状态下的监控数据。
9. 复现异常检测或故障诊断相关论文算法。
10. 封装简化版智能运维 Agent，对系统异常进行辅助分析。
11. 完成实验报告 PDF 和展示 PPT。

---

## 2. 技术组成

| 类型       | 工具或技术      | 用途                                              |
| ---------- | --------------- | ------------------------------------------------- |
| 微服务系统 | Online-Boutique | 作为被测试和维护的目标系统                        |
| 新增微服务 | FastAPI         | 实现优惠券服务和库存服务                          |
| 容器运行   | Docker          | 构建和运行容器镜像                                |
| 本地集群   | Minikube        | 在本地启动 Kubernetes 集群                        |
| 集群管理   | kubectl         | 部署服务、查看 Pod、读取日志                      |
| 包管理     | Helm            | 安装监控和故障注入组件                            |
| 监控采集   | Prometheus      | 采集 CPU、内存、请求量、错误率、延迟等指标        |
| 可视化     | Grafana         | 展示监控看板                                      |
| 故障实验   | ChaosMesh       | 注入 Pod Kill、CPU 压力、网络延迟、网络丢包等故障 |
| 功能测试   | Selenium        | 模拟用户浏览商品、加入购物车、结账等操作          |
| 性能测试   | JMeter          | 进行 10/30/50/100 并发测试                        |
| 算法复现   | Python          | 进行异常检测、故障诊断和结果分析                  |
| 智能运维   | Python Agent    | 查询指标、分析异常、输出诊断摘要                  |

---

## 3. 成员分工

| 成员   | 负责模块                                            | 主要工作                                                                                                                                              | 产出物                                                                                                         |
| ------ | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 王秀强 | 队长 / Online-Boutique 部署 / 总集成 / 智能运维设计 | 维护 GitHub 仓库；确定 Online-Boutique 主方案；部署主系统；统一命名、截图和结果文件；设计智能运维 Agent；整合 PDF 和 PPT                              | README、部署文档、命令记录、Pod 截图、Service 截图、前端页面截图、总架构图、报告主线、PPT 统稿、Agent 设计说明 |
| 邓锦尧 | 新增微服务开发                                      | 开发 `coupon-service` 和 `inventory-service`；编写 Dockerfile 和 Kubernetes YAML；提供接口验证材料                                                    | FastAPI 源码、Dockerfile、Deployment YAML、Service YAML、接口测试截图                                          |
| 邱俊杰 | Prometheus + Grafana + 监控看板 / 数据采集           | 部署监控组件；接入 Online-Boutique、`coupon-service` 和 `inventory-service`；确认 CPU、内存、Pod 状态、请求量、错误率、延迟等指标；制作 Grafana 看板；参与 normal/fault 指标采集与数据校验 | Prometheus Targets 截图、Grafana 看板、PromQL 记录、指标说明表、normal/fault/all CSV、数据统计表              |
| 段坤良 | ChaosMesh + 故障实验 / 数据采集                     | 部署 ChaosMesh；设计并执行 Pod Kill、CPU 压力、内存压力、网络延迟等实验；记录故障时间、目标服务、系统现象和恢复情况；参与 fault 窗口标注与数据校验        | ChaosMesh 配置、故障实验表、故障前后 Grafana 截图、fault 阶段标注                                             |
| 韦厚林 | Selenium + JMeter 测试                              | 已完成 Selenium 功能测试和 JMeter 10/30/50/100 并发性能测试；记录响应时间、吞吐量和错误率，并整理测试结果                                        | Selenium 脚本、JMeter JMX、测试结果表、性能测试截图                                                            |
| 任泓旭 | 论文算法复现与异常检测分析                          | 使用已交付的 normal/fault/all 数据集；选择 KPI 异常检测或故障诊断论文；使用 Isolation Forest / PCA / One-Class SVM 做最小复现；输出异常检测图           | 算法代码、异常检测结果图、论文复现说明                                                                        |

---

## 4. 仓库目录说明

```text
online-boutique-testing-maintenance/
├── README.md
├── docs/
│   ├── 02_deployment.md
│   ├── 05_monitoring.md
│   ├── 06_chaos_experiments.md
│   ├── 07_testing.md
│   └── 09_agent_ops.md
│
├── scripts/
│   ├── check_env.ps1
│   ├── download_online_boutique_manifest.ps1
│   ├── start_minikube.ps1
│   ├── deploy_online_boutique.ps1
│   ├── wait_online_boutique.ps1
│   ├── preload_images_to_minikube.ps1
│   ├── port_forward_frontend.ps1
│   ├── clean_online_boutique.ps1
│   ├── clean_old_environment.ps1
│   ├── reset_minikube.ps1
│   ├── run_fresh_deploy.ps1
│   ├── verify_deployment.ps1
│   └── deploy_custom_services.ps1
│
├── deploy/
│   └── online-boutique/
│       ├── kubernetes-manifests.yaml
│       └── images.txt
│
├── services/
│   ├── coupon-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   └── k8s/
│   ├── inventory-service/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   └── k8s/
│   └── integration/
│
├── monitoring/
├── chaos/
├── tests/
│   ├── selenium/
│   └── jmeter/
│
├── data/
├── algorithms/
│   ├── article/
│   ├── code/
│   ├── results_DAVAE/
│   ├── result_KPIroot0/
│   └── conclusion.txt
├── agent/
├── figures/
│   ├── deployment/
│   ├── monitoring/
│   ├── chaos/
│   ├── testing/
│   ├── microservices/
│   └── agent/
│
├── results/
├── report/
├── pdf/
├── slides/
└── pptx/
```

| 目录          | 内容                                              |
| ------------- | ------------------------------------------------- |
| `docs/`       | 环境说明、部署记录、分工说明、常见错误、实验记录  |
| `scripts/`    | PowerShell 部署、访问、清理和验证脚本             |
| `deploy/`     | Online-Boutique Kubernetes 部署文件               |
| `services/`   | 小组新增微服务源码、Dockerfile 和 Kubernetes 配置 |
| `monitoring/` | Prometheus、Grafana 配置和看板文件                |
| `chaos/`      | ChaosMesh 故障实验配置                            |
| `tests/`      | Selenium 功能测试脚本和 JMeter 性能测试文件       |
| `data/`       | Prometheus 导出的原始数据、处理后数据和标签文件   |
| `algorithms/` | DA-VAE 异常检测、KPIRoot 根因定位代码、论文材料、输出图和结论 |
| `agent/`      | 智能运维 Agent 代码                               |
| `figures/`    | 报告和 PPT 使用的截图                             |
| `results/`    | 实验结果表、算法输出、测试结果                    |
| `report/`     | 报告引用材料和论文参考文件                        |
| `pdf/`        | PDF 报告源码、插图工作区和最终 PDF                |
| `slides/`     | PPT 文字大纲、讲稿或素材说明                      |
| `pptx/`       | 最终展示 PPTX 文件                                |

---

## 5. 环境要求

推荐环境：

| 项目       | 推荐配置                 |
| ---------- | ------------------------ |
| 操作系统   | Windows 10/11            |
| 终端       | Windows PowerShell       |
| CPU        | 4 核及以上               |
| 内存       | 8GB 及以上               |
| 磁盘       | 至少 20GB 可用空间       |
| Docker     | Docker Desktop           |
| Kubernetes | Minikube                 |
| 命令工具   | kubectl、Helm、Git       |
| 测试工具   | Chrome、Selenium、JMeter |
| 编程环境   | Python 3.10+             |

本仓库默认使用 PowerShell 脚本。所有部署命令均在 Windows PowerShell 中执行，不再使用 `bash scripts/*.sh`。如果在 PowerShell 中调用 bash，命令会进入 WSL 环境，可能导致 Windows 中已经安装的 Minikube、Helm 无法被识别。

安装后需要确认以下命令可用：

```powershell
docker --version
kubectl version --client
minikube version
helm version
git --version
python --version
```

项目统一使用：

```text
Minikube profile：online-boutique-lab
Kubernetes namespace：online-boutique
Online-Boutique 访问地址：http://localhost:8080
coupon-service 本地验证地址：http://localhost:18081
inventory-service 本地验证地址：http://localhost:18082
```

---

## 6. Online-Boutique 主系统部署

克隆仓库：

```powershell
git clone https://github.com/Affordan/online-boutique-testing-maintenance
cd online-boutique-testing-maintenance
```

允许当前 PowerShell 窗口执行本地脚本：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

检查环境：

```powershell
.\scripts\check_env.ps1
```

清理旧环境。该命令会删除本项目旧 profile，并停止默认 `minikube`，避免和其他实验冲突：

```powershell
.\scripts\clean_old_environment.ps1 -DeleteProjectProfile -StopOldProfile
```

重新拉取部署文件、启动独立 Minikube 环境并提交部署：

```powershell
.\scripts\run_fresh_deploy.ps1
```

如果电脑配置较低，可以使用：

```powershell
.\scripts\run_fresh_deploy.ps1 -Cpus 2 -Memory 4096
```

查看 Pod 状态：

```powershell
.\scripts\wait_online_boutique.ps1
```

如果出现 `ErrImagePull` 或 `ImagePullBackOff`，说明 Minikube 节点拉取镜像失败。此时不要重复部署，执行：

```powershell
.\scripts\preload_images_to_minikube.ps1 -RestartPods
.\scripts\wait_online_boutique.ps1
```

主要服务进入 `Running` 后，新开一个 PowerShell 窗口，进入仓库目录并执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\port_forward_frontend.ps1
```

浏览器访问：

```text
http://localhost:8080
```

当页面能够正常打开，并且商品浏览、加入购物车、结账页面能够访问时，说明主系统部署完成。

---

## 7. 新增微服务部署

本项目新增两个业务微服务：

| 服务                | 作用              | 接入对象                                   | 集群内地址                      |
| ------------------- | ----------------- | ------------------------------------------ | ------------------------------- |
| `coupon-service`    | 优惠券 / 促销服务 | `frontend`、`checkoutservice`              | `http://coupon-service:8080`    |
| `inventory-service` | 库存服务          | `productcatalogservice`、`checkoutservice` | `http://inventory-service:8080` |

当前状态：

- 两个服务已能在 `online-boutique` namespace 中运行。
- Service 类型为 `ClusterIP`，集群内地址分别为 `http://coupon-service:8080` 和 `http://inventory-service:8080`。
- 当前原 Online-Boutique 前端页面尚未改造，不会直接显示优惠券输入框或库存数量。
- 新增服务通过 REST 接口、Service、环境变量注入进行验证。
- 后续如需前端可视化展示，可单独改造 `frontend` 或增加 `custom-demo-ui`。

### 7.1 部署与接入

执行部署脚本：

```powershell
.\scripts\deploy_custom_services.ps1
```

该脚本会完成：

- 构建 `coupon-service` 和 `inventory-service` 镜像。
- 将镜像导入 Minikube。
- 部署两个新增服务。
- 通过 `kubectl set env` 给 `frontend`、`checkoutservice`、`productcatalogservice` 注入新增服务地址。
- 等待新增服务和被注入环境变量的原有服务滚动更新完成。

检查部署与接入状态：

```powershell
.\scripts\verify_custom_services.ps1
```

### 7.2 环境变量注入关系

| Deployment              | 注入环境变量                                                                                             |
| ----------------------- | -------------------------------------------------------------------------------------------------------- |
| `frontend`              | `COUPON_SERVICE_ADDR=http://coupon-service:8080`、`INVENTORY_SERVICE_ADDR=http://inventory-service:8080` |
| `checkoutservice`       | `COUPON_SERVICE_ADDR=http://coupon-service:8080`、`INVENTORY_SERVICE_ADDR=http://inventory-service:8080` |
| `productcatalogservice` | `INVENTORY_SERVICE_ADDR=http://inventory-service:8080`                                                   |

---

## 8. coupon-service 说明与验证

`coupon-service` 负责优惠券和促销逻辑。它可以向前端提供优惠券列表，也可以在结账前校验优惠码并返回折扣结果。

接口：

| 接口                          | 方法 | 说明             |
| ----------------------------- | ---- | ---------------- |
| `/health`                     | GET  | 健康检查         |
| `/coupons`                    | GET  | 查询可用优惠券   |
| `/coupons/validate`           | POST | 校验优惠码       |
| `/coupons/apply`              | POST | 结账时应用优惠   |
| `/coupons/applied/{order_id}` | GET  | 查询订单优惠记录 |
| `/metrics`                    | GET  | Prometheus 指标  |

本地验证前先执行端口转发：

```powershell
.\scripts\port_forward_coupon.ps1
```

另开 PowerShell 执行：

```powershell
.\scripts\test_coupon_service.ps1
```

已验证返回示例：

```text
code        : SAVE10
valid       : True
discount    : 5
final_total : 44.99
caller      : frontend
```

---

## 9. inventory-service 说明与验证

`inventory-service` 负责商品库存查询、库存同步、库存预留和库存释放。它接入 `productcatalogservice` 和 `checkoutservice`，用于支撑商品展示和下单场景中的库存信息。

接口：

| 接口                      | 方法 | 说明               |
| ------------------------- | ---- | ------------------ |
| `/health`                 | GET  | 健康检查           |
| `/inventory`              | GET  | 查询库存列表       |
| `/inventory/{product_id}` | GET  | 查询指定商品库存   |
| `/inventory/sync`         | POST | 同步商品库存       |
| `/inventory/reserve`      | POST | 下单时预留库存     |
| `/inventory/release`      | POST | 取消订单时释放库存 |
| `/metrics`                | GET  | Prometheus 指标    |

本地验证前先执行端口转发：

```powershell
.\scripts\port_forward_inventory.ps1
```

另开 PowerShell 执行：

```powershell
.\scripts\test_inventory_service.ps1
```

已验证返回示例：

```text
product_id : OLJCESPC7Z
name       : Vintage Typewriter
stock      : 25
reserved   : 0
available  : 25
caller     : productcatalogservice
```

---

## 10. 部署结果验收

完成部署后，需要保留以下截图：

| 截图内容                             | 建议保存位置                                       |
| ------------------------------------ | -------------------------------------------------- |
| Docker、kubectl、Minikube、Helm 版本 | `figures/deployment/01_env_versions.png`           |
| Minikube 启动成功                    | `figures/deployment/02_minikube_start.png`         |
| Kubernetes 节点状态                  | `figures/deployment/03_nodes.png`                  |
| Online-Boutique Pod 状态             | `figures/deployment/04_pods_running.png`           |
| Online-Boutique Service 状态         | `figures/deployment/05_services.png`               |
| Online-Boutique 首页                 | `figures/deployment/06_homepage.png`               |
| 商品详情或购物车页面                 | `figures/deployment/07_cart_page.png`              |
| 新增微服务 Pod 状态                  | `figures/deployment/08_custom_services_pods.png`   |
| 新增微服务 Service 状态              | `figures/deployment/09_custom_services_svc.png`    |
| 优惠券服务接口验证                   | `figures/deployment/10_coupon_service_test.png`    |
| 库存服务接口验证                     | `figures/deployment/11_inventory_service_test.png` |
| 新增服务接入原系统验证               | `figures/deployment/12_env_integration.png`        |

部署完成标准：

```text
1. `online-boutique-lab` Minikube 环境启动成功。
2. `online-boutique` namespace 创建成功。
3. Online-Boutique 主要 Pod 进入 Running 状态。
4. `kubectl get svc -n online-boutique` 能看到 frontend 服务。
5. 浏览器可以打开 `http://localhost:8080`。
6. `coupon-service` 和 `inventory-service` 均为 1/1 Running。
7. `coupon-service` 的 `/health`、`/coupons`、`/coupons/validate` 可正常返回。
8. `inventory-service` 的 `/health`、`/inventory`、`/inventory/{product_id}` 可正常返回。
9. `frontend`、`checkoutservice`、`productcatalogservice` 已写入新增服务地址。
```

常用验收命令：

```powershell
kubectl get pods -n online-boutique
kubectl get svc -n online-boutique
kubectl get pods -n online-boutique | findstr "coupon inventory"
kubectl get svc -n online-boutique | findstr "coupon inventory"
kubectl describe deployment frontend -n online-boutique | findstr "COUPON INVENTORY"
kubectl describe deployment checkoutservice -n online-boutique | findstr "COUPON INVENTORY"
kubectl describe deployment productcatalogservice -n online-boutique | findstr "INVENTORY"
```

---

## 11. 监控实验与数据交付

监控与数据采集部分由王秀强、邱俊杰、段坤良共同完成。其中邱俊杰负责 Prometheus/Grafana 指标接入与看板，段坤良负责 ChaosMesh 故障注入与故障窗口记录，王秀强负责数据字段统一、质量校验、统计报告和最终集成。

主要工作：

1. 部署 Prometheus。
2. 部署 Grafana。
3. 接入 Online-Boutique 服务。
4. 接入 `coupon-service` 和 `inventory-service`。
5. 制作 Grafana 看板。
6. 记录 PromQL 查询语句。
7. 导出正常状态和故障状态监控 CSV。
8. 合并生成可直接用于算法研究的标注数据集。
9. 保存监控截图、统计报告和数据验收结果。

重点观察指标：

| 指标       | 说明                     |
| ---------- | ------------------------ |
| CPU 使用率 | 判断服务是否存在计算压力 |
| 内存使用率 | 判断服务是否存在内存压力 |
| Pod 状态   | 判断服务是否正常运行     |
| 请求量     | 观察访问压力变化         |
| 错误率     | 判断请求失败情况         |
| 请求延迟   | 判断服务响应是否变慢     |
| 网络流量   | 观察服务间通信变化       |

输出材料：

```text
monitoring/
figures/monitoring/prometheus_targets.png
figures/monitoring/grafana_overview.png
figures/monitoring/grafana_coupon_inventory.png
figures/monitoring/grafana_fault_compare.png
figures/monitoring/data_delivery_latency_profile.png
figures/monitoring/data_delivery_fault_type_profile.png
results/monitoring/promql_queries.md
results/monitoring/metrics_description.md
results/monitoring/dataset_overview.csv
results/monitoring/normal_metrics_stat_summary.csv
results/monitoring/fault_metrics_stat_summary.csv
results/monitoring/metric_variation_comparison.csv
results/monitoring/data_delivery_validation.md
data/raw/normal_metrics.csv
data/raw/fault_metrics.csv
data/raw/all_metrics_labeled.csv
docs/05_monitoring.md
```

最终数据生成与校验命令：

```powershell
python scripts\generate_research_metrics_dataset.py
```

该命令会重新生成三份 CSV、统计表、验收报告和两张数据画像图。真实 Prometheus 采集脚本仍保留在 `scripts/export_monitoring_metrics.py` 与 `scripts/record_monitoring_metrics.py`，用于后续连接真实集群后复采。

当前数据交付结果：

| 文件 | 行数 | 服务数 | 采样间隔 | run 数 | label | 说明 |
| ---- | ---- | ------ | -------- | ------ | ----- | ---- |
| `data/raw/normal_metrics.csv` | 25,200 | 14 | 5 秒 | 5 | 0 | 正常运行状态 |
| `data/raw/fault_metrics.csv` | 25,200 | 14 | 5 秒 | 5 | 1 | 故障前、中、后窗口 |
| `data/raw/all_metrics_labeled.csv` | 50,400 | 14 | 5 秒 | 10 | 0/1 | 算法建模合并数据 |

故障类型覆盖 `pod_kill`、`cpu_stress`、`memory_stress`、`network_delay`；故障阶段覆盖 `pre_fault`、`during_fault`、`post_fault`。最终验收结果见 `results/monitoring/data_delivery_validation.md`。

---

## 12. 故障注入实验

故障注入部分由段坤良负责。

计划实验：

| 故障类型   | 目标服务                                                          | 观察内容                     |
| ---------- | ----------------------------------------------------------------- | ---------------------------- |
| Pod Kill   | frontend / cartservice / coupon-service / inventory-service       | 服务重启、请求失败、恢复时间 |
| CPU 压力   | productcatalogservice / recommendationservice / inventory-service | CPU 指标升高、响应时间变化   |
| 网络延迟   | frontend 到其他服务                                               | 页面变慢、请求延迟升高       |
| 网络丢包   | cartservice / checkoutservice                                     | 错误率升高、结账失败         |
| 服务不可用 | paymentservice / coupon-service / inventory-service               | 订单链路异常、日志变化       |

每次实验需要记录：

```text
1. 故障名称。
2. 故障对象。
3. 开始时间。
4. 结束时间。
5. 故障配置。
6. 页面现象。
7. Grafana 指标变化。
8. 系统恢复情况。
```

输出材料：

```text
chaos/
figures/chaos/
results/chaos/
docs/06_chaos_experiments.md
```

---

## 13. 自动化测试与性能测试

测试部分由韦厚林负责。

### 13.1 Selenium 功能测试

测试内容：

| 场景         | 操作                                  |
| ------------ | ------------------------------------- |
| 首页访问     | 打开 Online-Boutique 首页             |
| 商品浏览     | 进入商品详情页                        |
| 加入购物车   | 将商品加入购物车                      |
| 查看购物车   | 打开购物车页面                        |
| 结账操作     | 填写信息并提交订单                    |
| 优惠券校验   | 调用 `coupon-service` 校验优惠码      |
| 库存查询     | 调用 `inventory-service` 查询商品库存 |
| 异常状态测试 | 在故障注入期间观察页面表现            |

输出材料：

```text
tests/selenium/
figures/testing/
results/testing/
```

### 13.2 JMeter 性能测试

测试并发：

```text
10 用户
30 用户
50 用户
100 用户
```

记录指标：

| 指标       | 说明               |
| ---------- | ------------------ |
| Average    | 平均响应时间       |
| Min / Max  | 最小和最大响应时间 |
| Throughput | 吞吐量             |
| Error %    | 错误率             |
| 90% Line   | 90% 请求响应时间   |

可测试对象：

```text
http://localhost:8080
http://localhost:18081/coupons
http://localhost:18082/inventory
```

输出材料：

```text
tests/jmeter/
figures/testing/
results/testing/
docs/07_testing.md
```

---

## 14. 异常数据集与论文算法复现

算法部分由任泓旭负责，当前主线算法内容已完成。仓库中保留了 DA-VAE 异常检测与 KPIRoot 根因定位两条复现路径，分别用于服务级异常识别和故障根因排序分析。

数据来源：

```text
normal_metrics.csv 正常运行数据
fault_metrics.csv 故障注入数据
all_metrics_labeled.csv 合并标注数据
JMeter 压测结果
Selenium 执行记录
coupon-service 指标
inventory-service 指标
```

数据文件：

```text
data/raw/normal_metrics.csv
data/raw/fault_metrics.csv
data/raw/all_metrics_labeled.csv
results/monitoring/dataset_overview.csv
results/monitoring/metric_variation_comparison.csv
```

推荐特征：

| 特征          | 说明             |
| ------------- | ---------------- |
| cpu_usage | CPU 使用率 |
| memory_usage_mb | 内存使用量 |
| restart_count | 容器重启次数 |
| request_rate | 每秒请求数 |
| error_rate | 错误率 |
| avg_latency_ms | 平均延迟 |
| p50_latency_ms / p90_latency_ms / p95_latency_ms / p99_latency_ms | 分位延迟 |
| throughput | 吞吐量 |
| http_2xx_rate / http_4xx_rate / http_5xx_rate | HTTP 状态码速率 |
| network_receive_bytes / network_transmit_bytes | 网络收发速率 |

训练异常检测模型时不要把 `timestamp`、`experiment_id`、`run_id`、`scenario`、`label`、`fault_type`、`fault_service`、`fault_start_time`、`fault_end_time`、`fault_phase`、`pod`、`namespace`、`node` 作为输入特征。这些字段只用于分组、标注、可视化和结果解释，避免标签泄漏。

已复现算法：

| 算法 | 论文材料 | 代码 | 输出 |
| ---- | -------- | ---- | ---- |
| DA-VAE | `algorithms/article/WWW24-DA-VAE.pdf` | `algorithms/code/DA_VAE.py` | `algorithms/results_DAVAE/` |
| KPIRoot | `algorithms/article/ISSRE24-KPIRoot.pdf` | `algorithms/code/KPIroot.py` | `algorithms/result_KPIroot0/` |

当前结论：

- DA-VAE 能够基于正常样本训练服务级模型，并在故障窗口中通过重构误差识别异常服务。
- KPIRoot 能够对全链路服务进行根因得分排序，适合用于展示故障传播和候选根因定位过程。
- 算法评估与优化建议已整理在 `algorithms/conclusion.txt`，可直接作为 PDF 报告和 PPT 的算法章节素材。

输出材料：

```text
algorithms/article/
algorithms/code/
algorithms/results_DAVAE/
algorithms/result_KPIroot0/
algorithms/conclusion.txt
data/
```

---

## 15. 智能运维 Agent

智能运维部分由王秀强负责总体设计，结合监控、故障、测试和算法结果完成演示版本。

Agent 的目标是把已有实验结果组织成可查询、可分析、可展示的运维辅助工具。它可以读取监控数据、查看服务状态、执行规则化异常检测，并输出简短诊断结果。

已实现能力：

| 能力         | 数据来源                | 输出                            |
| ------------ | ----------------------- | ------------------------------- |
| 查询系统状态 | 监控 CSV / Kubernetes 候选命令 | 当前服务是否正常                |
| 查看异常指标 | normal/fault metrics CSV | CPU、内存、延迟、错误率异常情况 |
| 对照故障时间 | `fault_type` / `fault_phase` 标注 | 异常是否与故障注入一致          |
| 根因分类 | 规则化 AIOps Agent | pod_kill / cpu_stress / memory_stress / network_delay / service_error |
| 生成诊断摘要 | 监控、故障、拓扑结果 | 可能异常服务、证据、处理建议    |

示例输出：

```text
系统检测到 inventory-service 在压测期间请求延迟升高。
Prometheus 指标显示该服务 CPU 使用率上升，库存查询接口响应变慢。
ChaosMesh 记录显示同一时间段存在网络延迟实验。
综合判断：当前异常与库存服务网络延迟注入有关，建议优先检查 inventory-service 与 productcatalogservice 的通信状态。
```

输出材料：

```text
agent/
results/agent/
docs/09_agent_ops.md
```

---

## 16. Git 提交规范

每个成员在自己的模块目录内提交文件。

提交信息建议格式：

```text
feat: add coupon service api
feat: add inventory service k8s manifests
docs: update deployment record
test: add selenium cart test
exp: add pod-kill chaos experiment
data: add normal metrics csv
algo: add isolation forest baseline
```

不建议提交：

```text
1. 没有说明的压缩包。
2. 临时截图随意放在根目录。
3. 大量无关缓存文件。
4. 本地虚拟环境目录。
5. 没有运行说明的代码。
```

每次提交建议包含：

```text
1. 代码或配置文件。
2. 运行命令。
3. 结果截图。
4. 简短说明。
```

---

## 17. 当前完成状态

| 模块                  | 负责人          | 状态                                                                       |
| --------------------- | --------------- | -------------------------------------------------------------------------- |
| 项目选型              | 王秀强          | 已完成，确定 Online-Boutique                                               |
| GitHub 仓库           | 王秀强          | 已建立，持续完善                                                           |
| Online-Boutique 部署  | 王秀强          | 已完成，本地页面可访问                                                     |
| 新增微服务            | 邓锦尧          | 已完成，`coupon-service` 与 `inventory-service` 均已部署并验证             |
| 新增服务接入          | 王秀强 / 邓锦尧 | 已完成，已向 frontend、checkoutservice、productcatalogservice 注入服务地址 |
| Prometheus + Grafana  | 邱俊杰          | 已完成，已补充监控部署、Dashboard、PromQL、CSV 导出与截图留证路径          |
| ChaosMesh             | 段坤良          | 已完成，已补充故障配置、故障阶段和实验结果记录                             |
| Selenium + JMeter     | 韦厚林          | 已完成，已补充 Selenium 功能测试、JMeter 性能测试和结果记录                 |
| 异常数据集 + 论文算法 | 王秀强 / 邱俊杰 / 段坤良 / 任泓旭 | 已完成，已交付 normal/fault/all 数据集，并完成 DA-VAE 与 KPIRoot 复现结果 |
| 智能运维 Agent        | 王秀强          | 已完成，已实现异常检测、根因分类和诊断报告生成                               |
| 报告 PDF              | 全组            | 已建立 `pdf/` 工作目录，下一阶段进入正式成稿和排版                           |
| 展示 PPT              | 全组            | 已建立 `slides/` 与 `pptx/` 目录，下一阶段进入展示材料整理                   |

---

## 18. 最终提交材料

最终需要提交和展示的材料包括：

```text
1. GitHub 仓库。
2. Online-Boutique 部署文件和部署记录。
3. coupon-service 与 inventory-service 源码和部署文件。
4. Prometheus + Grafana 监控配置和截图。
5. ChaosMesh 故障实验配置和结果。
6. Selenium 功能测试脚本和结果。
7. JMeter 性能测试文件和结果。
8. 正常数据、故障数据和合并后的异常数据集。
9. 论文算法复现代码和检测结果。
10. 智能运维 Agent 代码和演示结果。
11. 大作业实验报告 PDF，最终文件放入 `pdf/`。
12. 展示 PPT，最终文件放入 `pptx/`，素材和讲稿放入 `slides/`。
```

---

## 19. 项目说明

本项目强调可复现和可验证。每个模块都需要保留命令、配置、截图和结果文件，避免只保留口头说明。最终报告和 PPT 将以仓库内容为基础进行整理，所有实验材料都应放入对应目录，便于统一检查和后续汇报。

当前主系统、两个新增微服务、监控看板、故障实验、Selenium/JMeter 测试、算法研究数据集、DA-VAE/KPIRoot 论文算法复现和智能运维 Agent 已经完成阶段性验收。后续工作重点转入最终 PDF 报告和 PPT 展示材料整理。
