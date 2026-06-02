#!/bin/bash
set -euo pipefail

kubectl delete namespace online-boutique --ignore-not-found=true
