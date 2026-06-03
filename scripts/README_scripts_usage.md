# PowerShell 部署脚本说明

本脚本包适用于 Windows PowerShell。项目统一使用：

```text
Minikube profile: online-boutique-lab
Kubernetes namespace: online-boutique
```

## 常规部署

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\scripts\check_env.ps1
.\scripts\clean_old_environment.ps1 -DeleteProjectProfile -StopOldProfile
.\scripts\run_fresh_deploy.ps1
.\scripts\wait_online_boutique.ps1
```

主要 Pod 进入 `Running` 后，新开一个 PowerShell：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\port_forward_frontend.ps1
```

浏览器访问：

```text
http://localhost:8080
```

## 镜像拉取失败

如果 Pod 出现 `ImagePullBackOff` 或 `ErrImagePull`，执行：

```powershell
.\scripts\preload_images_to_minikube.ps1 -RestartPods
.\scripts\wait_online_boutique.ps1
```

## 常用检查

```powershell
.\scripts\verify_deployment.ps1
kubectl get pods -n online-boutique
kubectl get svc -n online-boutique
```

## 清理

```powershell
.\scripts\clean_online_boutique.ps1
.\scripts\reset_minikube.ps1
```
