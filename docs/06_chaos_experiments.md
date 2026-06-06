# ChaosMesh ����ע��ʵ���¼

���ļ�¼ Online-Boutique ΢����ϵͳ��ʹ�� ChaosMesh ���еĹ���ע��ʵ�顣

## 1. Ŀ��

ʹ�� ChaosMesh ��ϵͳ���й���ע��ʵ�飬��֤ϵͳ�����¹��ϳ����µ���Ϊ��

1. **Pod Kill** �� ɱ��Ŀ����� Pod����֤ Kubernetes �Զ��ָ�������
2. **CPU Stress** �� ��Ŀ�����ע�� CPU ѹ�����۲�����Ӱ�졣
3. **Network Delay** �� ��Ŀ�����ע�������ӳ٣���֤�������õ��ݴ��ԡ�

## 2. ǰ������

���� ChaosMesh ǰ��ȷ�ϣ�

`ash
bash scripts/check_env.sh
bash scripts/start_minikube.sh
bash scripts/deploy_online_boutique.sh
kubectl get pods -n online-boutique
`

ȷ�����з��� Pod ���� Running ״̬��

## 3. ��װ ChaosMesh

ʹ�� Helm ��װ ChaosMesh��

`ash
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update
kubectl create ns chaos-mesh
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh --version 2.7.0
`

��֤ ChaosMesh �������״̬��

`ash
kubectl get pods -n chaos-mesh
`

## 4. ʵ�����

����� 6 ������ע��ʵ�飬���� 3 �ֹ������� x 2 ��Ŀ�����

| ʵ���� | �������� | Ŀ����� | �����ļ� |
|---------|---------|---------|---------|
| F001 | Pod Kill | coupon-service | chaos/chaos_pod_kill_coupon.yaml |
| F002 | Pod Kill | inventory-service | chaos/chaos_pod_kill_inventory.yaml |
| F003 | CPU Stress | coupon-service | chaos/chaos_cpu_stress_coupon.yaml |
| F004 | Network Delay | inventory-service | chaos/chaos_network_delay_inventory.yaml |
| F005 | Network Delay | coupon-service | chaos/chaos_network_delay_coupon.yaml |
| F006 | CPU Stress | inventory-service | ✅ Completed |
| F007 | Network Loss | coupon-service | ✅ Completed |
| F008 | Network Loss | inventory-service | ✅ Completed |

## 5. ʵ��ִ�в���

### 5.1 ͨ�ò���

ÿ��ʵ�鰴���²���ִ�У�

1. Ӧ��ʵ�����ã�\kubectl apply -f chaos/<config-file>.yaml\
2. ��֤ʵ��״̬��\kubectl get <chaos-type> -n chaos-mesh\
3. �鿴ʵ�����飺\kubectl describe <chaos-type> <experiment-name> -n chaos-mesh\
4. ȷ��ע��ɹ���AllInjected: True��
5. ����ʵ�飺\kubectl delete <chaos-type> <experiment-name> -n chaos-mesh\

### 5.2 ע������

- ��ǰ ChaosMesh �汾�� PodChaos��StressChaos��NetworkChaos ����֧�� spec.scheduler �ֶΣ���� YAML ���Ƴ���
- NetworkChaos �� correlation �ֶ���ʹ���ַ������ͣ��� \"50"\�������������͡�
- ʵ��ע��ɹ�������ȴ����� duration������ʱ�ֶ������

## 6. ʵ����

ʵ��������� \esults/chaos/experiment_results.md\����ͼ�� \igures/chaos/\��

## 7. ��ͼ�嵥

| �ļ� | ˵�� |
|------|------|
| screenshot_01_all_pods_running.png | ��ʼ״̬ - ���� Pod ������ |
| screenshot_02_chaosmesh_pods.png | ChaosMesh ��� Pod |
| screenshot_03_f001_yaml.png | F001 YAML �������� |
| screenshot_04_f001_applied.png | F001 �����ɹ� |
| screenshot_05_f001_describe.png | F001 ʵ������ |
| screenshot_06_f002_describe.png | F002 ʵ������ |
| screenshot_07_f002_recovered.png | F002 �ָ�״̬ |
| screenshot_08_f002_deleted.png | F002 ������� |
| screenshot_09_f003_applied.png | F003 �����ɹ� |
| screenshot_10_f003_describe.png | F003 ʵ������ |
| screenshot_11_f003_deleted.png | F003 ������� |
| screenshot_12_f004_applied.png | F004 �����ɹ� |
| screenshot_13_f004_describe.png | F004 ʵ������ |
| screenshot_14_f004_deleted.png | F004 ������� |
| screenshot_15_f005_applied.png | F005 �����ɹ� |
| screenshot_16_f005_describe.png | F005 ʵ������ |
| screenshot_17_f005_deleted.png | F005 ������� |
| screenshot_18_f006_applied.png | F006 �����ɹ� |
| screenshot_19_f006_describe.png | F006 ʵ������ |
| screenshot_20_f006_deleted.png | F006 ������� |
| screenshot_21_f007_applied.png | F007 创建成功 |
| screenshot_22_f007_describe.png | F007 实验详情 |
| screenshot_23_f007_deleted.png | F007 清理完成 |
| screenshot_24_f008_applied.png | F008 创建成功 |
| screenshot_25_f008_describe.png | F008 实验详情 |
| screenshot_26_f008_deleted.png | F008 清理完成 |

