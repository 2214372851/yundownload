# 快速开始

## 版本说明

由于在 YunDownload V0.4.x 版本中，YunDownloader 处于性能原因 API 发生变化 所以抽离的两份快速开始文档。

变化如下：

- `YunDownloader` API已经移除采用全新实现
- 现在添加下载任务不会阻塞主线程，可以实现多文件异步下载

## 并发限制

对于大型资源下载，您可能需要使用对本地的连接限制来避免文件服务器过载。

您可以通过以下方式进行限制......

```python
from yundownload import DownloadPools

with DownloadPools(max_workers=5) as pool:
    ...
```

## 状态回调

在某些情况下我们需要下载成功或失败时完成后续操作。

```python
from yundownload import Request

Request(
    url='',
    save_path='',
    success_callback=print,
    error_callback=print
)
```

## 请求传参

目前 Yun download 可以在 `Request` 对象中传递。

```python
from yundownload import DownloadPools, Request

with DownloadPools() as pool:
    pool.push(Request(
        url='',
        save_path='',
        params={}
    ))
```

## 认证

对于部分需要在请求中校验身份信息的，需要通过 `auth` 携带身份信息。

```python
from yundownload import Auth, Request

Request(
    url='',
    save_path='',
    auth=Auth(username='', password='')
)
```

## 超时

在不同网络或不同站点下，由于网络波动、资源限制等问题需要改动超时时间，默认为 `20` 秒。

由于初衷是大文件下载，对于小文件可适当修改时间。

你可以在实例化下载器时传递全局参数，也可以在 `Request` 对象中传递。

```python
from yundownload import Request

Request(
    url='',
    save_path='',
    timeout=20
)
```

## 请求头

可以通过设置请求头来为请求携带一些信息如：`cookies` 、`Content-Type`等。

你可以在实例化下载器时传递全局参数，也可以在 `Request` 对象中传递。

```python
from yundownload import Request

Request(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    headers={'token': '***'}
)
```

## Cookies

当然你也可以将 `cookies` 放到请求头中。

你可以在实例化下载器时传递全局参数，也可以在 `Request` 对象中传递。

```python
from yundownload import Request

Request(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    cookies={'**': '***'}
)
```

## 流模式

默认模式为根据文件大小自动选择分片下载或流式限制，如果需要强制使用流模式，可以设置 `stream` 参数为 `True`。

你可以在实例化下载器时传递全局参数，也可以在 `Request` 对象中设置。

```python
from yundownload import Request

request = Request(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe'
)
request.stream = True
```

## 重定向

默认情况下，YunDownloader 会自动处理重定向，如果需要禁用重定向，可以将 `follow_redirects` 参数设置为 `False`。
否则就是最大重定向次数。

```python
from yundownload import Request

request = Request(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    follow_redirects=True
)
```

## 错误重试

YunDownloader 默认会自动重试下载，如果需要禁用重试，可以将 `retry` 参数设置为 `1` 或不传递。

```python
from yundownload import DownloadPools, Retry

with DownloadPools(retry=Retry(retry=2, retry_delay=10, retry_connect=10)) as poll:
    ...
```

## 证书

Yun download 默认会自动处理证书，如果需要禁用证书，可以将 `verify` 参数设置为 `False`。

```python
from yundownload import DownloadPools, Retry

with DownloadPools(verify=False) as poll:
    ...
```

## 代理

```python
from yundownload import DownloadPools, Proxies

with DownloadPools(proxies=Proxies(http='http://127.0.0.1:7890', https='http://127.0.0.1:7890')) as poll:
    ...
```

## 日志

Yun download 默认会禁用日志，如果需要显示日志，可以调用 `show_log`，并输出到控制台， `write_log(filepath)` 输出到文件，
`logger` 获取日志对象。

```python
from yundownload.logger import show_log, write_log, logger

```


## 进度条

Yun download cli 工具中实现。

```python
from yundownload import render_ui, Request

render_ui([Request(url='', save_path=''), ])
```

## 状态

通过 `request.status` 可获取当前执行状态。

```python
from yundownload import Request
request = Request(url='', save_path='')
print(request.status)
```

## 下载状态

通过 `request.stat` 可获取当前下载状态。

```python
from yundownload import Request

request = Request(url='', save_path='')
print('下载进度', request.stat.percentage)
print('每秒下载字节', request.stat.speed)
print('开始时间', request.stat.start_time)
print('结束时间', request.stat.end_time)
```