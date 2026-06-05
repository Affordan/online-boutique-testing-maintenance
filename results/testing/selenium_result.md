# Selenium 功能测试结果

## 测试环境

| 项目 | 内容 |
| --- | --- |
| 测试地址 | `http://localhost:8080` |
| 浏览器 | Chrome |
| 测试工具 | Selenium |
| 测试脚本 | `tests/selenium/selenium_test.py` |

## 测试场景

| 编号 | 场景 | 状态 | 说明 | 截图 |
| --- | --- | --- | --- | --- |
| T001-1 | 首页访问 | 通过 | 首页正常打开并完成截图 | `figures/testing/selenium_homepage.png` |
| T001-2 | 商品详情 | 通过 | 成功进入商品详情页并完成截图 | `figures/testing/selenium_product_detail.png` |
| T001-3 | 加入购物车 | 通过 | 商品成功加入购物车，购物车页面正常显示 | `figures/testing/selenium_cart.png` |
| T001-4 | 结账流程 | 通过 | 成功填写结账表单并提交订单 | `figures/testing/selenium_checkout.png` |
| T001-5 | 执行结果 | 通过 | Selenium 主流程执行结束，输出结果截图 | `figures/testing/selenium_result.png` |

## 执行结论

Selenium 主流程已执行通过，覆盖首页访问、商品详情、加入购物车、查看购物车和结账提交。执行过程中使用与当前 Chrome 匹配的本地 ChromeDriver。

本次截图均为浏览器视口截图，分辨率为 `2139x1241`，可用于报告和 PPT 展示。
