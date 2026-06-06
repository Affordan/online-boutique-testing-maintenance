#!/bin/bash
set -euo pipefail

kubectl port-forward svc/frontend 8080:80 -n online-boutique
