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
| 队长 + A | 你 | 总集成 + Online-Boutique 部署 | 维护仓库结构；确定主方案；部署 Online-Boutique；确认前端、Pod、Service 可用；记录部署问题与解决方案；统筹 README、架构图、任务看板、报告和 PPT | README、部署文档、命令记录、Pod 截图、Service 截图、前端页面截图、最终 PDF/PPT |
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

## 02 仓库建立当前状态

- 本地 Git 仓库已初始化。
- 已添加上游仓库地址：

```bash
git remote add upstream https://github.com/JoinFyc/Online-Boutique.git
```

如果需要把本地仓库推送到小组 GitHub 仓库，先在 GitHub 创建空仓库，然后执行：

```bash
git remote add origin https://github.com/<your-org-or-user>/<your-repo>.git
git branch -M main
git push -u origin main
```

## Online-Boutique 源码同步

如果网络可以访问 GitHub，推荐直接克隆目标仓库：

```bash
git clone https://github.com/JoinFyc/Online-Boutique.git
```

如果已经在本仓库内初始化，则可以尝试从上游同步：

```bash
git fetch upstream
git branch -r
```

看到上游分支后，按实际分支选择同步方式。例如：

```bash
git switch -c upstream-source upstream/main
```

或者：

```bash
git switch -c upstream-source upstream/release/v0.10.2
```

之后再把课程目录、README、报告材料合并到小组主分支。

## A 成员优先要做什么

你作为队长 + A，优先完成以下闭环：

1. 确认本地环境版本：

```bash
docker --version
kubectl version --client
minikube version
helm version
python --version
```

2. 启动 Minikube：

```bash
minikube start --cpus=4 --memory=4096 --driver=docker
kubectl get nodes
kubectl get pods -A
```

3. 部署 Online-Boutique。

如果源码已经同步到本地，优先使用仓库自带 manifest：

```bash
kubectl create namespace online-boutique
kubectl apply -n online-boutique -f ./release/kubernetes-manifests.yaml
kubectl wait --for=condition=available --timeout=300s -n online-boutique --all deployments
kubectl get pods -n online-boutique
kubectl get svc -n online-boutique
```

如果只是为了尽快跑通演示，也可以使用 Google 官方 microservices-demo 的预构建 manifest：

```bash
kubectl create namespace online-boutique
kubectl apply -n online-boutique -f https://github.com/GoogleCloudPlatform/microservices-demo/raw/main/release/kubernetes-manifests.yaml
kubectl wait --for=condition=available --timeout=300s -n online-boutique --all deployments
```

4. 访问前端：

```bash
minikube service frontend-external -n online-boutique
```

如果上面的方式不可用，使用端口转发：

```bash
kubectl port-forward -n online-boutique svc/frontend 8080:80
```

然后访问 <http://localhost:8080>。

5. 保存 A 需要交付的证据：

- `docker --version`、`kubectl version --client`、`minikube version`、`helm version` 截图或命令记录。
- `kubectl get nodes` 截图。
- `kubectl get pods -n online-boutique` 截图。
- `kubectl get svc -n online-boutique` 截图。
- Online-Boutique 前端页面截图。
- 部署问题与解决方案记录。

建议把截图放到 `figures/deploy/`，命令记录放到 `results/deploy/`。

## 部署需要 Google 的什么帮助

本作业如果使用 Minikube 本地部署，通常不需要 Google Cloud 账号，也不需要 GKE。Google 主要提供三类帮助：

1. Online-Boutique/microservices-demo 项目源码、Kubernetes manifest 和官方部署说明。
2. 公开容器镜像或预构建 manifest，便于快速部署到任意 Kubernetes 集群。
3. 可选的 GKE、Cloud Build、Artifact Registry/GCR 等云资源。如果要在 Google Cloud 上部署真实集群才需要这些；本课程本地 Minikube 跑通一般不需要。

因此，当前最推荐路线是：本地 Docker + Minikube + kubectl + Helm 跑通 Online-Boutique，后续再接 Prometheus/Grafana/ChaosMesh/JMeter/Selenium/Agent。

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

