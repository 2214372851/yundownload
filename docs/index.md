![Yun Download](images/pdx1.gif)
![Yun Download](images/pdx2.gif)
![Yun Download](images/pdx3.gif)
![Yun Download](images/pdx4.gif)
![Yun Download](images/pdx5.gif)
![Yun Download](images/pdx6.gif)
![Yun Download](images/pdx7.gif)

# Yun download

------

[![PyPI version](https://img.shields.io/pypi/v/yundownload)](https://pypi.org/project/yundownload/)

*Python 简易高效的文件下载器。*

Yun download 是 Python 3 的文件下载器，它提供流式下载和文件分片下载，并支持 动态并发。

------

## 安装

使用 pip 安装：

```
$ pip install yundownload
```

`Yun download` 需要 `Python 3.10+`

## 示例

现在，让我们开始第一个示例：

```python
from yundownload import Downloader, Resources


if __name__ == '__main__':
    with Downloader() as d:
        r1 = d.submit(Resources(
            uri="https://hf-mirror.com/cognitivecomputations/DeepSeek-R1-AWQ/resolve/main/model-00074-of-00074.safetensors?download=true",
            save_path="DeepSeek-R1-AWQ/model-00074-of-00074.safetensors"
        ))
        r2 = d.submit(Resources(
            uri='ftp://yunhai:admin123@192.168.6.99/data/spider_temp/0f03dc87-57ec-4278-bf95-15d4a1ad90d3.zip',
            save_path='0f03dc87-57ec-4278-bf95-15d4a1ad90d3.zip'
        ))
        r3 = d.submit(Resources(
            uri='sftp://root:20020308@192.168.6.99/root/quick_start.sh',
            save_path='quick_start.sh'
        ))
        r4 = d.submit(Resources(
            uri='https://c1.7bbffvip.com/video/xiantaiyoushu/%E7%AC%AC01%E9%9B%86/index.m3u8',
            save_path='./video/download.mp4',
            metadata={'test': 'test'}
        ))
    print(r1.result(), r2.result(), r3.result(), r4.result())
```

> 命令行在当前版本 `0.6.0-beta.1` 中尚未完成支持，将在后续完善此部分内容



## 特征

Yun download 建立在 `httpx` 模块上，并为您提供：

- 广泛的文件下载兼容
- 连接限速的连接分片加速
- 丰富的预留接口
- 同态控制并发数
- 断点续传(需文件服务器支持)
- 异常重试机制
- 完整的类型注释
- 命令行模式

当然一些 `httpx` 底层的特性，也继承而来



## 更多内容

要了解所有基础知识，请转到最新[快速入门](v6-quickstart.md)。



## 后续支持

- 命令行工具
- 分布式支持



## 问题相关

如果你在使用过程中发现问题欢迎提交Issue，如果问题很着急你也可以通过邮箱 `bybxbwg@foxmail.com` 与我取得联系



## 依赖项

`Yun download` 项目依赖于这些优秀的库：

- [httpx](https://github.com/projectdiscovery/httpx)- 网络请求。
- [aiofiles](https://github.com/Tinche/aiofiles)- 异步文件读写。
- [paramiko](https://github.com/paramiko/paramiko)- SSH协议连接。
- [m3u8](https://github.com/globocom/m3u8)- M3U8文件解析。
- [colorlog](https://github.com/borntyping/python-colorlog)- 彩色日志输出。
