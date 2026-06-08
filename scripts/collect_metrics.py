import argparse
import csv
import json
import subprocess
import sys
import time
from datetime import datetime
from urllib.request import urlopen, Request

KUBECTL = r'E:\桌面\大三下\软件测试与维护\kubectl\kubectl.exe'

CSV_FIELDS = [
    'timestamp', 'experiment_id', 'service', 'pod', 'scenario',
    'cpu_usage', 'memory_usage_mb', 'restart_count',
    'request_rate', 'error_rate', 'avg_latency_ms', 'p95_latency_ms',
    'throughput', 'http_2xx_rate', 'http_4xx_rate', 'http_5xx_rate',
    'network_receive_bytes', 'network_transmit_bytes',
]

def run_kubectl(args):
    result = subprocess.run([KUBECTL] + args, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        return None
    return result.stdout

def get_pod_data():
    \"\"\"从kubectl获取pod信息\"\"\"
    output = run_kubectl(['get', 'pods', '-n', 'online-boutique', '-o', 'json'])
    if not output:
        return {}
    data = json.loads(output)
    pods = {}
    for item in data.get('items', []):
        name = item['metadata']['name']
        labels = item['metadata'].get('labels', {})
        service = labels.get('app', 'unknown')
        containers = item.get('status', {}).get('containerStatuses', [])
        restart_count = sum(c.get('restartCount', 0) for c in containers)
        pods[name] = {'service': service, 'restart_count': restart_count}
    return pods

def parse_metrics(text):
    \"\"\"解析Prometheus文本格式的metrics\"\"\"
    result = {}
    for line in text.strip().split('\n'):
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0]
            value = parts[-1]
            # Extract labels
            if '{' in name:
                name = name.split('{')[0]
            try:
                result[name] = float(value)
            except ValueError:
                pass
    return result

def scrape_metrics(url):
    \"\"\"采集服务的/metrics端点\"\"\"
    req = Request(url, headers={'Accept': 'text/plain'})
    try:
        with urlopen(req, timeout=10) as resp:
            return parse_metrics(resp.read().decode('utf-8'))
    except Exception:
        return {}

def collect_snapshot(experiment_id, scenario):
    \"\"\"采集一次快照数据\"\"\"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pods = get_pod_data()
    
    # 采集 coupon-service metrics
    coupon_metrics = scrape_metrics('http://localhost:18081/metrics')
    inventory_metrics = scrape_metrics('http://localhost:18082/metrics')
    
    rows = []
    for pod_name, info in pods.items():
        service = info['service']
        if service not in ('coupon-service', 'inventory-service'):
            continue
        
        metrics = coupon_metrics if service == 'coupon-service' else inventory_metrics
        
        # 解析请求数据
        requests_total = metrics.get(f'{service.replace(\"-\", \"_\")}_requests_total', 0)
        duration_count = metrics.get(f'{service.replace(\"-\", \"_\")}_request_duration_seconds_count', 0)
        duration_sum = metrics.get(f'{service.replace(\"-\", \"_\")}_request_duration_seconds_sum', 0)
        
        row = {
            'timestamp': timestamp,
            'experiment_id': experiment_id,
            'service': service,
            'pod': pod_name,
            'scenario': scenario,
            'cpu_usage': metrics.get('process_cpu_seconds_total', 0),
            'memory_usage_mb': metrics.get('process_resident_memory_bytes', 0) / 1024 / 1024,
            'restart_count': info['restart_count'],
            'request_rate': requests_total,
            'error_rate': 0.0,
            'avg_latency_ms': (duration_sum / duration_count * 1000) if duration_count > 0 else 0,
            'p95_latency_ms': 0.0,
            'throughput': requests_total,
            'http_2xx_rate': requests_total,
            'http_4xx_rate': 0.0,
            'http_5xx_rate': 0.0,
            'network_receive_bytes': 0.0,
            'network_transmit_bytes': 0.0,
        }
        rows.append(row)
    
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment-id', default='EXP_001')
    parser.add_argument('--scenario', default='normal_traffic')
    parser.add_argument('--output', default='data/raw/normal_metrics.csv')
    parser.add_argument('--interval', type=int, default=10, help='采集间隔(秒)')
    parser.add_argument('--duration', type=int, default=5, help='采集次数')
    args = parser.parse_args()

    all_rows = []
    for i in range(args.duration):
        print(f'Collecting snapshot {i+1}/{args.duration}...')
        rows = collect_snapshot(args.experiment_id, args.scenario)
        all_rows.extend(rows)
        if i < args.duration - 1:
            time.sleep(args.interval)

    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f'Wrote {len(all_rows)} rows to {args.output}')

if __name__ == '__main__':
    main()
