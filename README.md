# Online-Boutique 软件测试与维护大作业

本仓库用于完成“软件测试与维护（2026 年春）”大作业。项目主线选择
[JoinFyc/Online-Boutique](https://github.com/JoinFyc/Online-Boutique)，围绕本地 Kubernetes/Minikube 部署、微服务扩展、监控、故障注入、自动化测试、异常检测算法复现和智能运维 Agent 展开。

## 项目目标

本组目标按“第三档 + 智能运维加分项”推进：

1. 在本地 Minikube 集群中跑通 Online-Boutique 原始微服务系统。
2. 新增 1-2 个微服务，并接入原系统或测试流程。
3. 部署 Prometheus、Grafana、ChaosMesh，完成监控与故障注入实验。
4. 使用 Selenium 和 JMeter 进行功能测试、性能测试和数据采集。
5. 使用采集到的正常/故障数据复现异常检测或故障诊断算法。
6. 实现简化智能运维 Agent，支持指标查询、异常判断、Pod/日志检查和诊断文本输出。

## 小组分工

| 角色 | 成员 | 负责模块 | 主要任务 | 关键产出 |
| --- | --- | --- | --- | --- |
| 队长 + A | 组长 | 总集成 + Online-Boutique 部署 | 维护仓库结构；确定主方案；部署 Online-Boutique；确认前端、Pod、Service 可用；记录部署问题与解决方案；统筹 README、架构图、任务看板、报告和 PPT | README、部署文档、命令记录、Pod 截图、Service 截图、前端页面截图、最终 PDF/PPT |
| B | 邓锦尧 | 新增微服务开发 | 开发 1-2 个新增服务，推荐 `ops-alert-service` 或 `user-log-service`；编写 Dockerfile、Deployment YAML、Service YAML；保证接口可访问 | FastAPI/Flask 源码、Dockerfile、K8s YAML、接口测试截图 |
| C | 邱俊杰 | Prometheus + Grafana + 监控看板 | 部署监控组件；接入 Online-Boutique 和新增服务；确认 CPU、内存、Pod 状态、请求量、错误率、延迟等指标；制作 Grafana 看板 | Prometheus Targets 截图、Grafana 看板、PromQL 记录、指标说明表 |
| D | 段坤良 | ChaosMesh + 故障实验 | 部署 ChaosMesh；设计 Pod Kill、CPU 压力、网络延迟、网络丢包等故障；记录故障前后现象与恢复情况 | ChaosMesh 配置、故障实验表、故障前后 Grafana 截图 |
| E | 韦厚林 | Selenium + JMeter 测试 | 编写 Selenium 脚本模拟浏览商品、加入购物车、结账；用 JMeter 做 10/30/50/100 并发测试；记录响应时间、吞吐量、错误率 | Selenium 脚本、JMeter JMX、测试结果表、性能测试截图 |
| F | 任泓旭 | 异常数据集 + 论文算法复现 | 从 Prometheus 导出正常/故障数据；合并数据集；选择 KPI 异常检测或故障诊断论文；用 Isolation Forest/PCA/One-Class SVM 等做最小复现 | normal/fault CSV、merged_dataset.csv、算法代码、异常检测结果图、论文复现说明 |

## 仓库目录

```text
.
├─ deploy/       # 原系统与新增服务部署 YAML
├─ services/     # 新增微服务源码与 Dockerfile
├─ monitoring/   # Prometheus、Grafana 配置与 Dashboard
├─ chaos/        # ChaosMesh 故障注入配置
├─ tests/        # Selenium、JMeter 脚本与结果
├─ data/         # normal、fault、merged 数据集
├─ algorithms/   # 异常检测与故障诊断复现代码
├─ agent/        # 智能运维助手代码
├─ figures/      # 报告和 PPT 使用的截图、图表
├─ results/      # 表格、CSV、JSON、诊断输出
├─ report/       # 大作业报告源文件与 PDF
└─ slides/       # 展示 PPT
```

## 快速开始

### 环境要求

```bash
docker --version
kubectl version --client
minikube version
helm version
python --version
```

### 启动 Minikube

```bash
minikube start --cpus=4 --memory=4096 --driver=docker
kubectl get nodes
kubectl get pods -A
```

### 部署 Online-Boutique

优先使用本仓库或上游仓库中的 Kubernetes manifest：

```bash
kubectl create namespace online-boutique
kubectl apply -n online-boutique -f ./release/kubernetes-manifests.yaml
kubectl wait --for=condition=available --timeout=300s -n online-boutique --all deployments
kubectl get pods -n online-boutique
kubectl get svc -n online-boutique
```

如需使用 Google 官方 microservices-demo 的预构建 manifest，可执行：

```bash
kubectl create namespace online-boutique
kubectl apply -n online-boutique -f https://github.com/GoogleCloudPlatform/microservices-demo/raw/main/release/kubernetes-manifests.yaml
kubectl wait --for=condition=available --timeout=300s -n online-boutique --all deployments
```

### 访问前端

```bash
minikube service frontend-external -n online-boutique
```

如果上面的方式不可用，可使用端口转发：

```bash
kubectl port-forward -n online-boutique svc/frontend 8080:80
```

然后访问 <http://localhost:8080>。

## 后续任务看板

| 阶段 | 编号 | 任务 | 负责人 | 状态 |
| --- | --- | --- | --- | --- |
| A | 01 | 确认选型为 Online-Boutique | 队长 + A | 已确定 |
| A | 02 | 建立 GitHub 仓库和目录结构 | 队长 + A | 进行中 |
| B | 03 | 本地基础环境准备 | A | 待开始 |
| B | 04 | Minikube 集群启动 | A | 待开始 |
| B | 05 | 原始 Online-Boutique 部署 | A | 待开始 |
| B | 06 | 系统服务结构梳理 | 队长 + A | 待开始 |
| C | 07-11 | 新增微服务开发与接入 | 邓锦尧 | 待开始 |
| D | 12-18 | 监控与故障注入 | 邱俊杰、段坤良 | 待开始 |
| E | 19-21 | Selenium/JMeter 测试与数据对齐 | 韦厚林 | 待开始 |
| F | 22-25 | 论文算法复现与结果分析 | 任泓旭 | 待开始 |
| G | 26-28 | 智能运维 Agent | 队长统筹，全组协作 | 待开始 |
| H | 29-32 | 报告、PPT、答辩材料收口 | 队长统筹，全组协作 | 待开始 |
