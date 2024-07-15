# 快速开始

首先，从导入 YunDownloader 开始：

```
>>> from yundownload import YunDownloader
```

现在，让我们尝试获实例一个下载器。

```
>>> download = YunDownloader(url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe', save_path='QQ9.7.17.29225.exe')
```

然后，我们需要启动下载器：

```
>>> download.run()
```

## 连接限制

对于大型资源下载，您可能需要使用对本地的连接限制来避免文件服务器过载。

您可以通过以下方式进行限制......

```python
from yundownload import YunDownloader, Limit

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    limit=Limit(
        max_concurrency=4,
        max_join=8
    )
)
```

> `limit` 参数只对文件分片下载有用，其中 `max_concurrency` 为最大并发数，`max_join` 为最大连接数。

## 状态回调

在某些情况下我们需要显示现在的下载进度等信息，可以通过回调实现进度的刷新。

回调函数需要包含两个参数 `state` 和  `meta`，其中 `state` 为当前的状态，例如进度等信息则在 `meta` 中。

```python
from yundownload import YunDownloader


def state_callback(state, meta):
    print(state, meta)


download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    update_callable=state_callback
)
```

## 请求传参

目前 Yun download 只支持 `GET` 请求的文件下载，所以在请求传参中只有 `params`。

```python
from yundownload import YunDownloader

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    params={
        'p1': '1'
    }
)
```

## 认证

对于部分需要在请求中校验身份信息的，需要通过 `auth` 携带身份信息。

```python
from yundownload import YunDownloader
from httpx import BasicAuth

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    auth=BasicAuth(username='root', password='12345')
)
```

## 超时

在不同网络或不同站点下，由于网络波动、资源限制等问题需要改动超时时间，默认为 `200` 秒。

由于初衷是大文件下载，对于小文件可适当修改时间。

```python
from yundownload import YunDownloader

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    timeout=60
)
```

## 请求头

可以通过设置请求头来为请求携带一些信息如：`cookies` 、`Content-Type`等。

```python
from yundownload import YunDownloader

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
)
```

## Cookies

当然你也可以将 `cookies` 放到请求头中。

```python
from yundownload import YunDownloader

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    cookies={
        'MUID': '1BC5BF370D78698B21F8AB910C1E6863'
    }
)
```

## 流模式

默认模式为根据文件大小自动选择分片下载或流式限制，如果需要强制使用流模式，可以设置 `stream` 参数为 `True`。

```python
from yundownload import YunDownloader

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    stream=True
)
```

## 重定向

默认情况下，YunDownloader 会自动处理重定向，如果需要禁用重定向，可以将 `max_redirects` 参数设置为 `0`。
否则就是最大重定向次数。

```python
from yundownload import YunDownloader

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    max_redirects=0
)
```

## 错误重试

第一层连接的错误重试默认开启，第二层连接的错误重试默认关闭。
YunDownloader 默认会自动重试下载，如果需要禁用重试，可以将 `error_retry` 参数设置为 `0`。

```python
from yundownload import YunDownloader

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    # 第一层连接重试
    retries=10
)
# 第二层下载重试
download.run(error_retry=2)

```

## 证书

Yun download 默认会自动处理证书，如果需要禁用证书，可以将 `verify` 参数设置为 `False`。

```python
from yundownload import YunDownloader

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    verify=False
)
```

## 代理
```python
from yundownload import YunDownloader
import httpx

proxies = {
    "http://": httpx.HTTPTransport(proxy="http://localhost:8030"),
    "https://": httpx.HTTPTransport(proxy="http://localhost:8031"),
}
download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    proxies=proxies
)
```