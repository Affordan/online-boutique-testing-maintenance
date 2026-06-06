# Selenium 功能测试

## 前置条件

需要保持 frontend 端口转发窗口运行：

```powershell
.\scripts\port_forward_frontend.ps1
```

测试地址：

```text
http://localhost:8080
```

## ChromeDriver

如果运行脚本时出现 `Unable to obtain driver for chrome`，说明 Selenium Manager 无法联网下载 ChromeDriver。此时需要手动准备与本机 Chrome 主版本一致的 `chromedriver.exe`，并通过环境变量指定路径。

示例：

```powershell
$env:CHROMEDRIVER_PATH="D:\tools\chromedriver\chromedriver.exe"
python tests\selenium\selenium_test.py
```

如果 Chrome 安装路径无法被自动识别，也可以指定浏览器路径：

```powershell
$env:CHROME_BINARY_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
$env:CHROMEDRIVER_PATH="D:\tools\chromedriver\chromedriver.exe"
python tests\selenium\selenium_test.py
```

## 输出截图

脚本会输出：

```text
figures/testing/selenium_homepage.png
figures/testing/selenium_product_detail.png
figures/testing/selenium_cart.png
figures/testing/selenium_checkout.png
figures/testing/selenium_result.png
```
