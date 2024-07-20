# 快速开始

## 版本说明
由于在 YunDownload V0.3.x 版本中，YunDownloader 的 API 发生变化 所以抽离的两份快速开始文档。

> 在实践中发现，YunDownload 在V0.1.x 与 V0.2.x 中每下载一个文件都会创建一个实例，其实创建实例并不是无法接受
> 
> 由于每次在需要下载新的文件时都会创建新的实例。
> 
> 但是实例之间的连接又是独立的，就导致每次实例都会创建连接池，这对服务器照成了压力，同时也降低了代码的执行效率
> 
> 所以我们不得不推翻之前的API

变化如下：

- `run` 方法已弃用，请使用 `download` 方法。
- `YunDownloader` 实例化时不再传递文件链接和保存路径，请在 `download` 方法中传递。

首先，从导入 YunDownloader 开始：

```
>>> from yundownload import YunDownloader
```

现在，让我们尝试获实例一个下载器。

```
>>> download = YunDownloader()
```

然后，我们需要启动下载器：

```
>>> download.download(url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe', save_path='QQ9.7.17.29225.exe')
```

## 连接限制

对于大型资源下载，您可能需要使用对本地的连接限制来避免文件服务器过载。

您可以通过以下方式进行限制......

```python
from yundownload import YunDownloader, Limit

download = YunDownloader(
    limit=Limit(
        max_concurrency=4,
        max_join=8
    )
)
download.download(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe'
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
    update_callable=state_callback
)
```

## 请求传参

目前 Yun download 只支持 `GET` 请求的文件下载，所以在请求传参中只有 `params`。

你可以在实例化下载器时传递全局参数，也可以在 `download` 方法中传递。

```python
from yundownload import YunDownloader

download = YunDownloader(
    params={
        'p1': '1'
    }
)

download.download(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    params={'p2': '2'}
)
```

## 认证

对于部分需要在请求中校验身份信息的，需要通过 `auth` 携带身份信息。

你可以在实例化下载器时传递全局参数，也可以在 `download` 方法中传递。

```python
from yundownload import YunDownloader
from httpx import BasicAuth

download = YunDownloader(
    auth=BasicAuth(username='root', password='12345')
)
download.download(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    auth=BasicAuth(username='root', password='12345')
)
```

## 超时

在不同网络或不同站点下，由于网络波动、资源限制等问题需要改动超时时间，默认为 `200` 秒。

由于初衷是大文件下载，对于小文件可适当修改时间。

你可以在实例化下载器时传递全局参数，也可以在 `download` 方法中传递。

```python
from yundownload import YunDownloader

download = YunDownloader(

    timeout=60
)
download.run(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    timeout=60
)
```

## 请求头

可以通过设置请求头来为请求携带一些信息如：`cookies` 、`Content-Type`等。

你可以在实例化下载器时传递全局参数，也可以在 `download` 方法中传递。

```python
from yundownload import YunDownloader

download = YunDownloader(
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
)
download.download(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    headers={'token': '***'}
)
```

## Cookies

当然你也可以将 `cookies` 放到请求头中。

你可以在实例化下载器时传递全局参数，也可以在 `download` 方法中传递。

```python
from yundownload import YunDownloader

download = YunDownloader(
    cookies={
        'MUID': '1BC5BF370D78698B21F8AB910C1E6863'
    }
)
download.download(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    save_path='QQ9.7.17.29225.exe',
    cookies={'**': '***'}
)
```

## 流模式

默认模式为根据文件大小自动选择分片下载或流式限制，如果需要强制使用流模式，可以设置 `stream` 参数为 `True`。

你可以在实例化下载器时传递全局参数，也可以在 `download` 方法中传递。

```python
from yundownload import YunDownloader

download = YunDownloader(
    stream=True
)
download.download(
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
    max_redirects=0
)
```

## 错误重试

第一层连接的错误重试默认开启，第二层连接的错误重试默认关闭。
YunDownloader 默认会自动重试下载，如果需要禁用重试，可以将 `error_retry` 参数设置为 `0` 或 `False`。

```python
from yundownload import YunDownloader

download = YunDownloader(
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
    proxies=proxies
)
```

## 日志

Yun download 默认会禁用日志，如果需要显示日志，可以将 `logger` 参数设置为 `logging.getLogger('yundownload')`，并输出到控制台。

```python
from yundownload import YunDownloader
import logging

logger = logging.getLogger('yundownload')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

download = YunDownloader()
```

## 动态并发

Yun download 默认会禁用动态并发，如果需要自动处理动态并发，可以将 `dynamic_concurrency` 参数设置为 `True`。

```python
from yundownload import YunDownloader

download = YunDownloader(
    dynamic_concurrency=True
)
```

## 进度条

Yun download 默认会禁用进度条，如果需要显示进度条，可以将 `cli` 参数设置为 `True`。

```python
from yundownload import YunDownloader

download = YunDownloader(
    cli=True
)
```