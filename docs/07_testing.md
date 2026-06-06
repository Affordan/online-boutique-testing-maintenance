# 自动化测试与性能测试记录

## 1. 测试目标

本模块用于构造 Online-Boutique、`coupon-service` 和 `inventory-service` 的功能测试与性能测试数据。测试输出需要同时支持报告展示、监控曲线采集、故障注入观察和后续算法数据合并。

当前采用“API 保底 + 前端增强”的策略：

```text
前端未完成新增业务接入时：Selenium 覆盖原有主流程，JMeter 直接压测新增服务 API。
前端完成新增业务接入后：Selenium 补充优惠券输入、折扣展示、库存展示和库存不足场景。
```

## 2. 当前验证状态

| 验证对象 | 验证内容 | 状态 | 结果记录 |
| --- | --- | --- | --- |
| Online-Boutique 主系统 | Pod 状态、首页、商品详情、购物车、结账页面可访问 | 已完成 | `results/testing/manual_environment_check.md` |
| coupon-service | `GET /health`、`GET /coupons`、`POST /coupons/validate` | 已完成 | `results/testing/manual_environment_check.md` |
| inventory-service | `GET /health`、`GET /inventory`、`GET /inventory/OLJCESPC7Z` | 已完成 | `results/testing/manual_environment_check.md` |

## 3. 交付文件

| 文件 | 内容 | 状态 |
| --- | --- | --- |
| `tests/selenium/selenium_test.py` | Selenium 自动化功能测试脚本 | 已执行 |
| `figures/testing/selenium_result.png` | Selenium 执行结果截图 | 已生成 |
| `tests/jmeter/online_boutique_test_plan.jmx` | JMeter 测试计划 | 已执行 |
| `results/testing/jmeter_results.csv` | JMeter 请求级原始结果，供数据合并使用 | 已生成 |
| `results/testing/jmeter_summary.csv` | 按并发档位汇总后的性能结果 | 已生成 |
| `figures/testing/` | JMeter 聚合报告、响应时间、吞吐量截图 | 已生成 |
| `tests/jmeter/test_description.md` | 测试对象、场景、并发设置说明 | 已创建 |

## 4. Selenium 测试场景

| 场景编号 | 场景名称 | 目标服务 | 当前策略 |
| --- | --- | --- | --- |
| T001 | 正常浏览与加购 | frontend/cart/productcatalog | 执行 |
| T002 | 优惠券使用 | frontend/coupon-service | 前端未接入时暂不做 UI 断言 |
| T003 | 库存查询 | frontend/inventory-service | 前端未接入时暂不做 UI 断言 |

当前 Selenium 主流程：

```text
打开首页 -> 进入商品详情 -> 加入购物车 -> 打开购物车 -> 填写结账信息 -> 提交订单
```

## 5. JMeter 测试场景

| 场景编号 | 场景名称 | 并发数 | 持续时间 | 目标服务 | 输出 |
| --- | --- | ---: | ---: | --- | --- |
| T004 | 低并发压测 | 10 | 10 min | frontend/coupon/inventory | CSV + 图 |
| T005 | 中并发压测 | 30 | 10 min | frontend/coupon/inventory | CSV + 图 |
| T006 | 高并发压测 | 50 | 10-15 min | frontend/coupon/inventory | CSV + 图 |
| T007 | 极限并发压测 | 100 | 10-15 min | frontend/coupon/inventory | CSV + 图 |
| T008 | 故障期间压测 | 30/50/100 | 与故障实验同步 | coupon/inventory | CSV + 图 |

JMeter 覆盖接口：

```text
GET  http://localhost:8080/
GET  http://localhost:8080/product/OLJCESPC7Z
GET  http://localhost:8080/cart
GET  http://localhost:18081/health
GET  http://localhost:18081/coupons
POST http://localhost:18081/coupons/validate
GET  http://localhost:18082/health
GET  http://localhost:18082/inventory
GET  http://localhost:18082/inventory/OLJCESPC7Z
```

## 6. 数据规范

`results/testing/jmeter_results.csv` 表头：

```text
timestamp,experiment_id,scenario,service,endpoint,concurrent_users,response_time_ms,latency_ms,success,status_code,error_message,throughput,bytes_sent,bytes_received
```

`results/testing/jmeter_summary.csv` 表头：

```text
experiment_id,scenario,service,endpoint,concurrent_users,samples,average_ms,min_ms,max_ms,p90_ms,throughput,error_percent
```

时间格式统一使用：

```text
YYYY-MM-DD HH:MM:SS
```

## 7. 当前限制

当前新增服务已经完成接口级验证，但前端 UI 是否实际调用 `coupon-service` 和 `inventory-service`，取决于前端返工完成情况。因此现阶段的新增服务测试以 JMeter API 压测为准，Selenium 新增业务场景在前端完成后补测。

## 8. 当前执行记录

### 8.1 Selenium 主流程

Selenium 主流程已执行通过，结果记录见：

```text
results/testing/selenium_result.md
```

已生成截图：

```text
figures/testing/selenium_homepage.png
figures/testing/selenium_product_detail.png
figures/testing/selenium_cart.png
figures/testing/selenium_checkout.png
figures/testing/selenium_result.png
```

### 8.2 JMeter 四档正常压测汇总

已完成 10、30、50、100 用户四档正常压测，并按统一数据规范合并生成最终结果文件。

| experiment_id | scenario | 并发用户 | 持续时间 | 总样本数 | 平均吞吐量 | 错误率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `EXP_NORMAL_001` | `jmeter_10_users` | 10 | 600 s | 5730 | 9.566/s | 0.00% |
| `EXP_NORMAL_002` | `jmeter_30_users` | 30 | 600 s | 17036 | 28.441/s | 0.00% |
| `EXP_NORMAL_003` | `jmeter_50_users` | 50 | 900 s | 42978 | 47.806/s | 0.00% |
| `EXP_NORMAL_004` | `jmeter_100_users` | 100 | 900 s | 85479 | 95.082/s | 0.00% |

最终请求级结果：

```text
results/testing/jmeter_results.csv
```

最终汇总结果：

```text
results/testing/jmeter_summary.csv
```

正式压测覆盖的服务请求量如下：

| service | 请求数 |
| --- | ---: |
| `frontend` | 50564 |
| `coupon-service` | 50372 |
| `inventory-service` | 50287 |

### 8.3 JMeter 截图材料

已保存 JMeter 相关截图：

| 截图 | 内容 |
| --- | --- |
| `figures/testing/jmeter_summary_10_30_50_100.png` | 四档并发压测汇总结果，包含 average、max、p90、throughput、error_percent |
| `figures/testing/jmeter_summary_100.png` | 100 用户 Summary Report，展示样本数、平均响应时间、错误率、吞吐量 |
| `figures/testing/jmeter_aggregate_report.png` | 100 用户 Aggregate Report，展示 90%/95%/99% Line、Error%、Throughput |
| `figures/testing/jmeter_response_time.png` | 100 用户响应时间曲线 |
| `figures/testing/jmeter_throughput.png` | 100 用户 Graph Results，包含 Throughput 指标 |
