# Online-Boutique 部署记录

## 环境信息

- OS:
- Docker:
- kubectl:
- Minikube:
- Helm:

## 部署命令

```bash
bash scripts/check_env.sh
bash scripts/start_minikube.sh
bash scripts/deploy_online_boutique.sh
bash scripts/port_forward_frontend.sh
```

## 部署结果

- Pod 状态：
- Service 状态：
- 前端访问地址：[http://localhost:8080](http://localhost:8080)
- 是否成功打开页面：
- 遇到的问题：
- 解决方法：

## 首次验证记录

验证时间：2026-06-02

已完成：

- `deploy/online-boutique/kubernetes-manifests.yaml` 已下载到仓库。
- `scripts/check_env.sh` 可执行，并能输出 Docker、kubectl、Minikube、Helm、Git、Python 版本。
- Docker Desktop 启动后，Docker daemon 可访问。
- Minikube 已启动，节点状态为 `Ready`。
- `online-boutique` 命名空间已创建，Deployment 和 Service 已应用。

当前阻塞：

- 多数 Pod 停留在 `ContainerCreating`，事件显示正在拉取 `us-central1-docker.pkg.dev/google-samples/microservices-demo/...:v0.10.5` 镜像。
- 宿主机执行 `docker pull us-central1-docker.pkg.dev/google-samples/microservices-demo/frontend:v0.10.5` 时出现 `EOF`，说明当前网络访问 Google Artifact Registry 不稳定。

建议处理：

- 确认 Docker Desktop 已启动。
- 如果在 Windows 上运行脚本，优先使用 Git Bash；如果使用 WSL2，需要打开 Docker Desktop 的 WSL integration。
- 如 Pod 长时间停留在 `ContainerCreating` 或出现 `ImagePullBackOff`，优先检查镜像仓库访问和网络代理。
- 当前仓库提供 `deploy/online-boutique/kubernetes-manifests-cn.yaml`，将 Google Artifact Registry 镜像替换为国内更容易访问的镜像源；`scripts/deploy_online_boutique.sh` 默认使用该文件。
- 本地集群状态混乱时，可先确认是否需要保留旧实验资源；确认不需要后再执行 `minikube delete` 重建集群。
