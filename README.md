# Online-Boutique 微服务测试与维护大作业

本仓库用于《软件测试与维护》课程大作业。项目选择 Online-Boutique 作为实验对象，围绕微服务系统完成部署、监控、故障注入、自动化测试、性能测试、异常数据采集、论文算法复现，并在原系统基础上新增微服务，进一步完成智能运维实验。

Online-Boutique 是一个典型的在线商店系统，包含前端、商品目录、购物车、结算、支付、推荐、邮件、广告、负载生成等服务。它的业务关系清楚，服务数量适中，适合用于观察微服务之间的调用关系、运行状态变化和故障传播现象。

本项目暂不使用 Google Cloud，采用本地 Kubernetes 环境完成部署。课程实验的重点在于系统部署、测试、维护、故障注入和异常分析，本地 Minikube 环境已经能够满足主要实验需求，同时可以避免云平台账号、计费、权限和网络访问带来的额外成本。所有成员统一按照本仓库说明在本地复现实验环境，保证实验过程可复现、材料可追溯、结果可整合。

---

## 1. 项目目标

本项目围绕 Online-Boutique 完成以下工作：

1. 在本地 Kubernetes 环境中部署 Online-Boutique 微服务系统。
2. 梳理系统服务组成、服务职责和核心业务请求。
3. 新增 1–2 个微服务，增强系统的日志采集和运维告警能力。
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

| 类型 | 工具或技术 | 用途 |
|---|---|---|
| 微服务系统 | Online-Boutique | 作为被测试和维护的目标系统 |
| 容器运行 | Docker | 运行容器镜像 |
| 本地集群 | Minikube | 在本地启动 Kubernetes 集群 |
| 集群管理 | kubectl | 部署服务、查看 Pod、读取日志 |
| 包管理 | Helm | 安装监控和故障注入组件 |
| 监控采集 | Prometheus | 采集 CPU、内存、请求量、错误率、延迟等指标 |
| 可视化 | Grafana | 展示监控看板 |
| 故障实验 | ChaosMesh | 注入 Pod Kill、CPU 压力、网络延迟、网络丢包等故障 |
| 功能测试 | Selenium | 模拟用户浏览商品、加入购物车、结账等操作 |
| 性能测试 | JMeter | 进行 10/30/50/100 并发测试 |
| 算法复现 | Python | 进行异常检测、故障诊断和结果分析 |
| 智能运维 | Python Agent | 查询指标、分析异常、输出诊断摘要 |

---

## 3. 成员分工

| 成员 | 负责模块 | 主要工作 | 产出物 |
|---|---|---|---|
| 王秀强 | 队长 / Online-Boutique 部署 / 总集成 / 智能运维设计 | 维护 GitHub 仓库结构；确定 Online-Boutique 主方案；部署主系统；统一命名、截图和结果文件；设计智能运维 Agent 的功能边界；整合 PDF 和 PPT | README、部署文档、命令记录、Pod 截图、Service 截图、前端页面截图、总架构图、任务看板、报告主线、PPT 统稿、Agent 设计说明 |
| 邓锦尧 | 新增微服务开发 | 开发 1–2 个新增服务，推荐实现 `ops-alert-service` 异常告警服务和 `user-log-service` 用户行为日志服务；编写 Dockerfile 和 K8s YAML；保证接口可访问 | FastAPI/Flask 源码、Dockerfile、Deployment YAML、Service YAML、接口测试截图 |
| 邱俊杰 | Prometheus + Grafana + 监控看板 | 部署监控组件；接入 Online-Boutique 和新增微服务；确认 CPU、内存、Pod 状态、请求量、错误率、延迟等指标；制作 Grafana 看板 | Prometheus Targets 截图、Grafana 看板、PromQL 记录、指标说明表 |
| 段坤良 | ChaosMesh + 故障实验 | 部署 ChaosMesh；设计并执行 Pod Kill、CPU 压力、网络延迟、网络丢包等实验；记录故障时间、目标服务、系统现象和恢复情况 | ChaosMesh 配置、故障实验表、故障前后 Grafana 截图 |
| 韦厚林 | Selenium + JMeter 测试 | 使用 Selenium 模拟用户浏览商品、加入购物车、结账；使用 JMeter 进行 10/30/50/100 并发测试；记录响应时间、吞吐量和错误率 | Selenium 脚本、JMeter JMX、测试结果表、性能测试截图 |
| 任泓旭 | 异常数据集 + 论文算法复现 | 从 Prometheus 导出正常和故障数据；合并数据集；选择 KPI 异常检测或故障诊断论文；使用 Isolation Forest / PCA / One-Class SVM 做最小复现；输出异常检测图 | normal/fault CSV、merged_dataset.csv、算法代码、异常检测结果图、论文复现说明 |

---

## 4. 仓库目录说明

```text
online-boutique-testing-maintenance/
├── README.md
├── docs/
│   ├── 01_environment.md
│   ├── 02_deployment.md
│   ├── 03_team_division.md
│   ├── 04_common_errors.md
│   ├── 05_monitoring.md
│   ├── 06_chaos_experiments.md
│   ├── 07_testing.md
│   ├── 08_algorithm.md
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
│   └── verify_deployment.ps1
│
├── deploy/
│   └── online-boutique/
│       └── kubernetes-manifests.yaml
│
├── services/
│   ├── ops-alert-service/
│   └── user-log-service/
│
├── monitoring/
│   ├── prometheus/
│   └── grafana/
│
├── chaos/
│   ├── pod-kill/
│   ├── cpu-stress/
│   ├── network-delay/
│   └── network-loss/
│
├── tests/
│   ├── selenium/
│   └── jmeter/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── labels/
│
├── algorithms/
├── agent/
├── figures/
│   ├── deployment/
│   ├── monitoring/
│   ├── chaos/
│   ├── testing/
│   └── algorithm/
│
├── results/
├── report/
└── ppt/
```

目录用途说明：

| 目录 | 内容 |
|---|---|
| `docs/` | 环境说明、部署记录、分工说明、常见错误、实验记录 |
| `scripts/` | 一键检查、启动、部署、访问、清理脚本 |
| `deploy/` | Online-Boutique 和后续 Kubernetes 部署文件 |
| `services/` | 小组新增微服务源码和部署文件 |
| `monitoring/` | Prometheus、Grafana 配置和看板文件 |
| `chaos/` | ChaosMesh 故障实验配置 |
| `tests/` | Selenium 功能测试脚本和 JMeter 性能测试文件 |
| `data/` | Prometheus 导出的原始数据、处理后数据和标签文件 |
| `algorithms/` | 异常检测和故障诊断算法代码 |
| `agent/` | 智能运维 Agent 代码 |
| `figures/` | 报告和 PPT 使用的截图 |
| `results/` | 实验结果表、算法输出、测试结果 |
| `report/` | 大作业 PDF 报告材料 |
| `ppt/` | 展示 PPT 材料 |

---

## 5. 环境要求

推荐环境：

| 项目 | 推荐配置 |
|---|---|
| 操作系统 | Windows 10/11 |
| 终端 | Windows PowerShell |
| CPU | 4 核及以上 |
| 内存 | 8GB 及以上 |
| 磁盘 | 至少 20GB 可用空间 |
| Docker | Docker Desktop |
| Kubernetes | Minikube |
| 命令工具 | kubectl、Helm、Git |
| 测试工具 | Chrome、Selenium、JMeter |
| 编程环境 | Python 3.10+ |

本仓库默认使用 PowerShell 脚本，所有部署命令均在 Windows PowerShell 中执行，不再使用 `bash scripts/*.sh`。如果在 PowerShell 中调用 bash，命令会进入 WSL 环境，可能导致 Windows 中已经安装的 Minikube、Helm 无法被识别。

安装后需要确认以下命令可用：

```powershell
docker --version
kubectl version --client
minikube version
helm version
git --version
python --version
```

项目统一环境：

```text
Minikube profile：online-boutique-lab
Kubernetes namespace：online-boutique
访问地址：http://localhost:8080
```

---

## 6. 快速运行

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

清理旧环境。该命令会删除本项目旧 profile，并停止默认 `minikube`，避免和以前实验冲突：

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

## 7. PowerShell 脚本说明

本项目脚本均放在 `scripts/` 目录下。

| 脚本 | 作用 |
|---|---|
| `check_env.ps1` | 检查 Docker、kubectl、Minikube、Helm、Git、Python 是否可用 |
| `download_online_boutique_manifest.ps1` | 下载 Online-Boutique 的 Kubernetes 部署文件 |
| `start_minikube.ps1` | 启动 `online-boutique-lab` 独立 Minikube 环境 |
| `deploy_online_boutique.ps1` | 创建 namespace 并部署 Online-Boutique |
| `wait_online_boutique.ps1` | 持续观察 Pod 状态 |
| `preload_images_to_minikube.ps1` | 将 Docker 镜像导入 Minikube，用于处理镜像拉取失败 |
| `port_forward_frontend.ps1` | 将 frontend 服务转发到 `http://localhost:8080` |
| `clean_online_boutique.ps1` | 删除 `online-boutique` namespace |
| `clean_old_environment.ps1` | 清理旧 profile、停止默认 profile |
| `reset_minikube.ps1` | 删除本项目 Minikube profile |
| `run_fresh_deploy.ps1` | 完成下载、启动、部署的组合执行 |
| `verify_deployment.ps1` | 输出当前节点、Pod、Service 状态 |

常用命令：

```powershell
.\scripts\verify_deployment.ps1
kubectl get pods -n online-boutique
kubectl get svc -n online-boutique
```

如果环境已经混乱，可以删除本项目独立环境后重来：

```powershell
.\scripts\reset_minikube.ps1
.\scripts\run_fresh_deploy.ps1
```

---

## 8. 部署结果验收

完成部署后，需要保留以下截图：

| 截图内容 | 建议保存位置 |
|---|---|
| Docker、kubectl、Minikube、Helm 版本 | `figures/deployment/01_env_versions.png` |
| Minikube 启动成功 | `figures/deployment/02_minikube_start.png` |
| Kubernetes 节点状态 | `figures/deployment/03_nodes.png` |
| Online-Boutique Pod 状态 | `figures/deployment/04_pods_running.png` |
| Online-Boutique Service 状态 | `figures/deployment/05_services.png` |
| Online-Boutique 首页 | `figures/deployment/06_homepage.png` |
| 商品详情或购物车页面 | `figures/deployment/07_cart_page.png` |

部署完成的基本标准：

```text
1. `online-boutique-lab` Minikube 环境启动成功。
2. `online-boutique` namespace 创建成功。
3. Online-Boutique 主要 Pod 进入 Running 状态。
4. `kubectl get svc -n online-boutique` 能看到 frontend 服务。
5. `port_forward_frontend.ps1` 能正常转发端口。
6. 浏览器可以打开 `http://localhost:8080`。
7. 商品浏览、购物车、结账页面能够正常访问。
```

本次部署中出现过 Google Artifact Registry 镜像拉取失败，报错表现为：

```text
ErrImagePull
ImagePullBackOff
Get "https://us-central1-docker.pkg.dev/v2/": EOF
```

处理方法是先用 Windows Docker 拉取镜像，再用 `minikube image load` 导入 `online-boutique-lab`。本仓库已将该处理写入 `preload_images_to_minikube.ps1`，后续成员遇到相同问题时可直接复用。

---


## 9. 新增微服务设计

本项目计划新增 1–2 个微服务，用于满足第三档要求，并服务于后续智能运维实验。

### 9.1 ops-alert-service

`ops-alert-service` 用于读取 Prometheus 指标，并根据 CPU、内存、错误率、请求延迟等指标输出异常告警结果。

建议接口：

| 接口 | 说明 |
|---|---|
| `GET /health` | 检查服务是否正常 |
| `GET /metrics-summary` | 返回核心指标摘要 |
| `GET /alerts` | 返回当前异常告警 |
| `POST /check` | 触发一次异常检查 |

返回示例：

```json
{
  "service": "frontend",
  "status": "anomaly",
  "reason": "request latency exceeds threshold",
  "latency": 1.82,
  "threshold": 1.00
}
```

### 9.2 user-log-service

`user-log-service` 用于记录用户行为和测试行为，包括浏览商品、加入购物车、结账、请求失败、响应时间等。

建议接口：

| 接口 | 说明 |
|---|---|
| `GET /health` | 检查服务是否正常 |
| `POST /log` | 写入一条用户行为日志 |
| `GET /logs` | 查询日志 |
| `GET /stats` | 返回行为统计结果 |

日志示例：

```json
{
  "user_id": "test-user-001",
  "action": "add_to_cart",
  "service": "frontend",
  "timestamp": "2026-06-01 10:00:00",
  "response_time": 0.42,
  "status": "success"
}
```

新增微服务交付要求：

```text
1. 服务源码。
2. requirements.txt 或对应依赖文件。
3. Dockerfile。
4. Kubernetes Deployment YAML。
5. Kubernetes Service YAML。
6. 接口说明。
7. 本地运行截图。
8. Kubernetes 部署截图。
```

---

## 10. 监控实验

监控部分由邱俊杰负责。

主要工作：

1. 部署 Prometheus。
2. 部署 Grafana。
3. 接入 Online-Boutique 服务。
4. 接入新增微服务。
5. 制作 Grafana 看板。
6. 记录 PromQL 查询语句。
7. 保存监控截图。

重点观察指标：

| 指标 | 说明 |
|---|---|
| CPU 使用率 | 判断服务是否存在计算压力 |
| 内存使用率 | 判断服务是否存在内存压力 |
| Pod 状态 | 判断服务是否正常运行 |
| 请求量 | 观察访问压力变化 |
| 错误率 | 判断请求失败情况 |
| 请求延迟 | 判断服务响应是否变慢 |
| 网络流量 | 观察服务间通信变化 |

输出材料：

```text
monitoring/
figures/monitoring/
results/monitoring/
docs/05_monitoring.md
```

---

## 11. 故障注入实验

故障注入部分由段坤良负责。

计划实验：

| 故障类型 | 目标服务 | 观察内容 |
|---|---|---|
| Pod Kill | frontend / cartservice / recommendationservice | 服务重启、请求失败、恢复时间 |
| CPU 压力 | productcatalogservice / recommendationservice | CPU 指标升高、响应时间变化 |
| 网络延迟 | frontend 到其他服务 | 页面变慢、请求延迟升高 |
| 网络丢包 | cartservice / checkoutservice | 错误率升高、结账失败 |
| 服务不可用 | paymentservice / emailservice | 订单链路异常、日志变化 |

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

## 12. 自动化测试与性能测试

测试部分由韦厚林负责。

### 12.1 Selenium 功能测试

测试内容：

| 场景 | 操作 |
|---|---|
| 首页访问 | 打开 Online-Boutique 首页 |
| 商品浏览 | 进入商品详情页 |
| 加入购物车 | 将商品加入购物车 |
| 查看购物车 | 打开购物车页面 |
| 结账操作 | 填写信息并提交订单 |
| 异常状态测试 | 在故障注入期间观察页面表现 |

输出材料：

```text
tests/selenium/
figures/testing/
results/testing/
```

### 12.2 JMeter 性能测试

测试并发：

```text
10 用户
30 用户
50 用户
100 用户
```

记录指标：

| 指标 | 说明 |
|---|---|
| Average | 平均响应时间 |
| Min / Max | 最小和最大响应时间 |
| Throughput | 吞吐量 |
| Error % | 错误率 |
| 90% Line | 90% 请求响应时间 |

输出材料：

```text
tests/jmeter/
figures/testing/
results/testing/
docs/07_testing.md
```

---

## 13. 异常数据集与论文算法复现

算法部分由任泓旭负责。

数据来源：

```text
Prometheus 正常运行数据
Prometheus 故障注入数据
JMeter 压测结果
Selenium 执行记录
user-log-service 行为日志
```

数据文件建议：

```text
data/raw/normal_metrics.csv
data/raw/fault_metrics.csv
data/processed/merged_dataset.csv
data/labels/fault_labels.csv
```

推荐特征：

| 特征 | 说明 |
|---|---|
| timestamp | 时间 |
| service | 服务名称 |
| cpu_usage | CPU 使用率 |
| memory_usage | 内存使用率 |
| request_count | 请求量 |
| error_count | 错误请求数 |
| latency | 请求延迟 |
| throughput | 吞吐量 |
| label | normal / anomaly |

可选算法：

| 算法 | 说明 |
|---|---|
| Isolation Forest | 适合做基础异常检测 |
| PCA | 适合观察多指标偏离 |
| One-Class SVM | 适合单类异常检测 |
| LSTM AutoEncoder | 适合时间序列异常检测，难度更高 |

输出材料：

```text
algorithms/
data/
figures/algorithm/
results/algorithm/
docs/08_algorithm.md
```

---

## 14. 智能运维 Agent

智能运维部分由王秀强负责总体设计，结合监控、故障、算法结果完成演示版本。

Agent 的目标不是替代完整运维平台，而是在已有实验基础上做一个可运行的辅助工具。它可以读取监控数据、查看服务状态、调用异常检测算法，并输出简短诊断结果。

计划能力：

| 能力 | 数据来源 | 输出 |
|---|---|---|
| 查询系统状态 | Kubernetes / Prometheus | 当前服务是否正常 |
| 查看异常指标 | Prometheus | CPU、内存、延迟、错误率异常情况 |
| 对照故障时间 | ChaosMesh 实验记录 | 异常是否与故障注入一致 |
| 调用检测算法 | algorithms/ | 异常时间点和异常分数 |
| 生成诊断摘要 | 监控、故障、算法结果 | 可能异常服务、证据、处理建议 |

示例输出：

```text
系统检测到 frontend 服务在 10:31 后请求延迟明显升高。
Prometheus 指标显示该服务 CPU 使用率上升，错误率同步增加。
ChaosMesh 记录显示同一时间段存在网络延迟实验。
综合判断：当前异常与网络延迟注入有关，建议优先检查 frontend 与下游服务之间的通信状态。
```

输出材料：

```text
agent/
figures/agent/
results/agent/
docs/09_agent_ops.md
```

---

## 15. Git 提交规范

每个成员在自己的模块目录内提交文件。

提交信息建议格式：

```text
feat: add ops-alert-service basic api
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

## 16. 当前完成状态

| 模块 | 负责人 | 状态 |
|---|---|---|
| 项目选型 | 王秀强 | 已确定 Online-Boutique |
| GitHub 仓库 | 王秀强 | 已建立，目录结构已完成 |
| Online-Boutique 部署 | 王秀强 | 已完成，本地页面可访问 |
| PowerShell 部署脚本 | 王秀强 | 已完成，支持独立 profile、清理、部署、镜像导入、端口转发 |
| 新增微服务 | 邓锦尧 | 待开始 |
| Prometheus + Grafana | 邱俊杰 | 待开始 |
| ChaosMesh | 段坤良 | 待开始 |
| Selenium + JMeter | 韦厚林 | 待开始 |
| 异常数据集 + 论文算法 | 任泓旭 | 待开始 |
| 智能运维 Agent | 王秀强 | 待设计 |
| 报告 PDF | 全组 | 后期整合 |
| 展示 PPT | 全组 | 后期整合 |

---

## 17. 最终提交材料

最终需要提交和展示的材料包括：

```text
1. GitHub 仓库。
2. Online-Boutique 部署文件和部署记录。
3. 新增微服务源码和部署文件。
4. Prometheus + Grafana 监控配置和截图。
5. ChaosMesh 故障实验配置和结果。
6. Selenium 功能测试脚本和结果。
7. JMeter 性能测试文件和结果。
8. 正常数据、故障数据和合并后的异常数据集。
9. 论文算法复现代码和检测结果。
10. 智能运维 Agent 代码和演示结果。
11. 大作业实验报告 PDF。
12. 展示 PPT。
```

---

## 18. 项目说明

本项目强调可复现和可验证。每个模块都需要保留命令、配置、截图和结果文件，避免只保留口头说明。最终报告和 PPT 将以仓库内容为基础进行整理，所有实验材料都应尽量放入对应目录，便于统一检查和后续汇报。

本仓库后续会持续补充部署记录、监控看板、故障实验、测试结果、算法分析和智能运维演示内容。
