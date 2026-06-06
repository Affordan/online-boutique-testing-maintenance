# Chaos Experiment Results

> experiments/figures/chaos ¼ÇÂ¼

## F001 - Pod Kill (coupon-service)

**Command:** kubectl apply -f chaos/chaos_pod_kill_coupon.yaml

**Config:**
- Action: pod-kill
- Target: coupon-service (app: coupon-service)
- Mode: one
- Duration: 10m

**Describe Output:**
`
Name:         pod-kill-coupon-f001
Namespace:    chaos-mesh
API Version:  chaos-mesh.org/v1alpha1
Kind:         PodChaos
Spec:
  Action:    pod-kill
  Duration:  10m
  Mode:      one
  Selector:
    Label Selectors:
      App:  coupon-service
    Namespaces:
      online-boutique
Status:
  Conditions:
    Status:  True
    Type:    Selected
    Status:  True
    Type:    AllInjected
    Status:  False
    Type:    AllRecovered
  Experiment:
    Container Records:
      Events:
        Operation:      Apply
        Timestamp:      2026-06-06T12:48:40Z
        Type:           Succeeded
      Id:               online-boutique/coupon-service-78f984b8f8-flkbv
      Injected Count:   1
      Phase:            Injected
Events:
  Normal  Applied  records  Successfully apply chaos
`

**Result:** Pod coupon-service-78f984b8f8-flkbv was killed successfully. Kubernetes Deployment auto-restarted a new Pod. ?

---

## F002 - Pod Kill (inventory-service)

**Command:** kubectl apply -f chaos/chaos_pod_kill_inventory.yaml

**Config:**
- Action: pod-kill
- Target: inventory-service (app: inventory-service)
- Mode: one
- Duration: 10m

**Describe Output:**
`
Name:         pod-kill-inventory-f002
Namespace:    chaos-mesh
API Version:  chaos-mesh.org/v1alpha1
Kind:         PodChaos
Spec:
  Action:    pod-kill
  Duration:  10m
  Mode:      one
  Selector:
    Label Selectors:
      App:  inventory-service
    Namespaces:
      online-boutique
Status:
  Conditions:
    Status:  True
    Type:    Selected
    Status:  True
    Type:    AllInjected
    Status:  False
    Type:    AllRecovered
  Experiment:
    Container Records:
      Events:
        Operation:      Apply
        Timestamp:      2026-06-06T14:21:21Z
        Type:           Succeeded
      Id:               online-boutique/inventory-service-6b76bf85fb-4dzsx
      Injected Count:   1
      Phase:            Injected
Events:
  Normal  Applied  records  Successfully apply chaos
`

**Result:** Pod inventory-service-6b76bf85fb-4dzsx was killed successfully. ?

---

## F003 - CPU Stress (coupon-service)

**Command:** kubectl apply -f chaos/chaos_cpu_stress_coupon.yaml

**Config:**
- Kind: StressChaos
- Action: cpu stress
- Target: coupon-service (app: coupon-service)
- Workers: 1, Load: 80%
- Duration: 15m

**Result:** CPU stress (80% load) injected to coupon-service Pod successfully. ?

---

## F004 - Network Delay (inventory-service)

**Command:** kubectl apply -f chaos/chaos_network_delay_inventory.yaml

**Config:**
- Kind: NetworkChaos
- Action: delay
- Target: inventory-service (app: inventory-service)
- Latency: 3000ms, Jitter: 1000ms, Correlation: 50%
- Duration: 15m

**Describe Output:**
`
Name:         network-delay-inventory-f004
Namespace:    chaos-mesh
API Version:  chaos-mesh.org/v1alpha1
Kind:         NetworkChaos
Spec:
  Action:  delay
  Delay:
    Correlation:  50
    Jitter:       1000ms
    Latency:      3000ms
  Duration:       15m
  Mode:           one
  Selector:
    Label Selectors:
      App:  inventory-service
    Namespaces:
      online-boutique
Status:
  Conditions:
    Status:  True
    Type:    Selected
    Status:  True
    Type:    AllInjected
  Experiment:
    Container Records:
      Events:
        Operation:      Apply
        Timestamp:      2026-06-06T15:24:28Z
        Type:           Succeeded
      Id:               online-boutique/inventory-service-6b76bf85fb-w9ls6
      Injected Count:   1
      Phase:            Injected
  Instances:
    online-boutique/inventory-service-6b76bf85fb-w9ls6:  1
Events:
  Normal  Applied  records  Successfully apply chaos
`

**Result:** 3000ms network delay injected to inventory-service Pod successfully. ?

---

## F005 - Network Delay (coupon-service)

**Command:** kubectl apply -f chaos/chaos_network_delay_coupon.yaml

**Config:**
- Kind: NetworkChaos
- Action: delay
- Target: coupon-service (app: coupon-service)
- Latency: 3000ms, Jitter: 1000ms, Correlation: 50%
- Duration: 15m

**Describe Output:**
`
Name:         network-delay-coupon-f005
Namespace:    chaos-mesh
API Version:  chaos-mesh.org/v1alpha1
Kind:         NetworkChaos
Spec:
  Action:  delay
  Delay:
    Correlation:  50
    Jitter:       1000ms
    Latency:      3000ms
  Duration:       15m
  Mode:           one
  Selector:
    Label Selectors:
      App:  coupon-service
    Namespaces:
      online-boutique
Status:
  Conditions:
    Status:  True
    Type:    Selected
    Status:  True
    Type:    AllInjected
  Experiment:
    Container Records:
      Events:
        Operation:      Apply
        Timestamp:      2026-06-06T15:45:46Z
        Type:           Succeeded
      Id:               online-boutique/coupon-service-78f984b8f8-srg7n
      Injected Count:   1
      Phase:            Injected
  Instances:
    online-boutique/coupon-service-78f984b8f8-srg7n:  1
Events:
  Normal  Applied  records  Successfully apply chaos
`

**Result:** 3000ms network delay injected to coupon-service Pod successfully. ?

---

## F006 - CPU Stress (inventory-service)

**Command:** kubectl apply -f chaos/chaos_cpu_stress_inventory.yaml

**Config:**
- Kind: StressChaos
- Action: cpu stress
- Target: inventory-service (app: inventory-service)
- Workers: 1, Load: 80%
- Duration: 15m

**Result:** CPU stress (80% load) injected to inventory-service Pod successfully. ?

---

## Summary

| Experiment | Type | Target | Status |
|------------|------|--------|--------|
| F001 | Pod Kill | coupon-service | ? Completed |
| F002 | Pod Kill | inventory-service | ? Completed |
| F003 | CPU Stress | coupon-service | ? Completed |
| F004 | Network Delay (3s) | inventory-service | ? Completed |
| F005 | Network Delay (3s) | coupon-service | ? Completed |
| F006 | CPU Stress | inventory-service | ? Completed |

All 6 chaos experiments were successfully executed and cleaned up. Experiment screenshots are saved in igures/chaos/.
