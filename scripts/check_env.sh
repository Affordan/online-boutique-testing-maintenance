#!/bin/bash
set -u

echo "Checking environment..."

docker --version || echo "Docker not found"
docker info >/dev/null 2>&1 || echo "Docker daemon not running or not reachable"
kubectl version --client || echo "kubectl not found"
minikube version || echo "Minikube not found"
helm version || echo "Helm not found"
git --version || echo "Git not found"
python --version || python3 --version || echo "Python not found"

echo "Environment check finished."
