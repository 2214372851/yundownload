![HTTPX](https://raw.githubusercontent.com/encode/httpx/master/docs/img/butterfly.png)

# Yun download

------

[![PyPI version](https://badge.fury.io/py/yundownload.svg)](https://badge.fury.io/py/yundownload)

*Python 简易高效的文件下载器。*

Yun download 是 Python 3 的文件下载器，它提供流式下载和文件分片下载，并支持 动态并发。

------

使用 pip 安装 Yun download：

`$ pip install yundownlaod`

现在，让我们开始第一个示例：

```shell
>>> import yundownlaod
>>> y = yundownload.YunDownloader('https://bing.com', './bing.html')
>>> y.run()
```

或者，使用命令行的方式：

> 命令行已经内置无需安装，使用前请确保当前环境已经安装 Yun download，命令行模式具有局限性，对于有一定要求的文件下载不建议使用

```shell
$ yundownload --help

usage: yundownload [-h] [-mc MAX_CONCURRENCY] [-mj MAX_JOIN] [-t TIMEOUT] [-r RETRY] [--stream]
                   url save_path

Yun Downloader

positional arguments:
  url                   Download url
  save_path             Save path, including file name

options:
  -h, --help            show this help message and exit
  -mc MAX_CONCURRENCY, --max_concurrency MAX_CONCURRENCY
                        Maximum concurrency
  -mj MAX_JOIN, --max_join MAX_JOIN
                        Maximum connection number
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout period
  -r RETRY, --retry RETRY
                        Retry times
  --stream              Forced streaming
```

命令行下载文件

```shell
$ yundownload 'https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe' './1.exe'

QQ9.7.17.29225.exe:   6%|██████▎                      | 13.6M/214M [00:05<01:15, 2.65MB/s] 
```

## 特征

Yun download 建立在 `httpx` 模块上，并为您提供：

- 广泛的文件下载兼容
- 连接限速的连接分片加速
- 丰富的预留接口
- 同态控制并发数
- 断点续传(需文件服务器支持)
- 双层重试机制
- 完整的类型注释

以及所有 `httpx` 及 `requests` 的标注功能

- 广泛[兼容请求的 API](https://www.python-httpx.org/compatibility/)。
- 标准同步接口，但[如果您需要，也可以提供异步支持](https://www.python-httpx.org/async/)。
- HTTP/1.1[和 HTTP/2 支持](https://www.python-httpx.org/http2/)。
- 能够直接向[WSGI 应用程序](https://www.python-httpx.org/async/#calling-into-python-web-apps)
  或[ASGI 应用程序](https://www.python-httpx.org/async/#calling-into-python-web-apps)发出请求。
- 到处都有严格的超时限制。
- 完整类型注释。
- 100％测试覆盖率。
- 国际域名和 URL
- 保持活动和连接池
- 具有 Cookie 持久性的会话
- 浏览器样式的 SSL 验证
- 基本/摘要身份验证
- 优雅的键/值 Cookie
- 自动减压
- 自动内容解码
- Unicode 响应主体
- 分段文件上传
- HTTP(S) 代理支持
- 连接超时
- 流式下载
- .netrc 支持
- 分块请求

## 文档
pip install mkdocs 
pip install mkdocs-material
要了解所有基础知识，请转到[快速入门](quickstart.md)。

## 依赖项

HTTPX 项目依赖于这些优秀的库：

- `httpx`- 网络请求。
- `tqdm`-命令行进度条。
- `certifi`-SSL 证书。
- `idna`- 国际化域名支持。
- `sniffio`- 异步库自动检测。

`Yun download` 部分思路来源于 `Scrapy` 提供的大量设计灵感。

## 安装

使用 pip 安装：

```
$ pip install yundownload
```

Yun download 需要 Python 3.10+