# YunDownload 代理功能使用指南

YunDownload 现在支持自动检测和使用系统代理设置，使得在需要通过代理访问网络的场景下更加方便。

## 功能特点

1. **自动检测系统代理**：支持 Windows、macOS 和 Linux 系统的代理设置
2. **环境变量支持**：自动检测 `HTTP_PROXY`、`HTTPS_PROXY` 和 `ALL_PROXY` 环境变量
3. **手动代理设置**：支持显式设置代理，会覆盖系统代理
4. **全面协议支持**：HTTP 和 M3U8 下载都支持代理功能

## 使用方法

### 1. 自动使用系统代理（推荐）

不设置任何代理参数，下载器会自动检测并使用系统代理：

```python
from yundownload import Downloader, Resources

# 创建资源对象，不设置代理
resources = Resources(
    uri="https://example.com/file.zip",
    save_path="file.zip"
)

# 下载文件（会自动使用系统代理）
with Downloader() as downloader:
    result = downloader.submit(resources)
```

### 2. 通过环境变量设置代理

设置环境变量后，下载器会自动使用：

```bash
# 在终端中设置环境变量
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# 然后运行你的Python脚本
python download_script.py
```

或者在Python脚本中设置：

```python
import os
from yundownload import Downloader, Resources

# 设置环境变量
os.environ['HTTP_PROXY'] = 'http://proxy.example.com:8080'
os.environ['HTTPS_PROXY'] = 'http://proxy.example.com:8080'

# 创建资源对象，不设置代理（会自动使用环境变量代理）
resources = Resources(
    uri="https://example.com/file.zip",
    save_path="file.zip"
)

# 下载文件
with Downloader() as downloader:
    result = downloader.submit(resources)
```

### 3. 显式设置代理

如果需要覆盖系统代理设置，可以显式指定：

```python
from yundownload import Downloader, Resources

# 创建资源对象，显式设置代理
resources = Resources(
    uri="https://example.com/file.zip",
    save_path="file.zip",
    http_proxy={
        'http': 'http://custom-proxy:8080',
        'https': 'http://custom-proxy:8080'
    }
)

# 下载文件（使用自定义代理）
with Downloader() as downloader:
    result = downloader.submit(resources)
```

## 代理优先级

代理设置的优先级从高到低为：

1. 显式设置的代理（`Resources.http_proxy`）
2. 环境变量中的代理设置
3. 系统代理设置

## 支持的代理格式

支持以下代理格式：

- HTTP 代理：`http://proxy.example.com:8080`
- HTTPS 代理：`https://proxy.example.com:8080`
- SOCKS 代理：`socks5://proxy.example.com:1080`

## 系统代理检测

### Windows

自动从注册表读取 Internet 设置中的代理配置。

### macOS

使用 `networksetup` 命令获取网络代理设置。

### Linux

主要通过环境变量检测代理设置。

## 注意事项

1. 如果设置了无效的代理，下载可能会失败
2. 代理设置会在日志中显示，方便调试
3. M3U8 下载的所有片段都会使用相同的代理设置
4. 如果不需要使用代理，确保系统、环境变量和代码中都没有设置代理

## 示例脚本

查看 `example_proxy_usage.py` 文件获取更多使用示例。

## 故障排除

如果代理不工作，可以：

1. 检查代理服务器是否可用
2. 验证代理地址和端口是否正确
3. 查看下载日志中的代理配置信息
4. 尝试手动设置代理而不是依赖自动检测