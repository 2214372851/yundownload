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

使用 pip 安装 Yun download：

`$ pip install yundownload`

现在，让我们开始第一个示例：

```python
from yundownload import DownloadPools, Request


with DownloadPools() as pool:
    pool.push(Request(
      url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
      save_path='./1.exe'
    ))
```

或者，使用命令行的方式：

> 命令行已经内置无需安装，使用前请确保当前环境已经安装 Yun download，命令行模式具有局限性，对于有一定要求的文件下载不建议使用

```shell
$ yundownload --help

usage: yundownload [-h] {load,download} ...

Yun Downloader

positional arguments:
  {load,download}
    load           Load a request
    download       Download a file

options:
  -h, --help       show this help message and exit
```

命令行下载文件

```shell
$ yundownload download 'https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe' './1.exe'

QQ9.7.17.29225.exe:   6%|██████▎                      | 13.6M/214M [00:05<01:15, 2.65MB/s] 
```

yfd文件命令行读取下载（只适用于简单场景）
```shell
$ yundownload load ./test.yfd
```

fyd文件格式
```text
save_path1<yfd>download_url1
save_path2<yfd>download_url2
```

## 特征

Yun download 建立在 `niquests` 模块上，并为您提供：

- 广泛的文件下载兼容
- 连接限速的连接分片加速
- 丰富的预留接口
- 同态控制并发数
- 断点续传(需文件服务器支持)
- 异常重试机制
- 完整的类型注释
- 命令行模式

当然一些 `niquests` 底层的特性，也继承而来


## 文档

要了解所有基础知识，请转到最新[快速入门](v3-quickstart.md)。

## 依赖项

`Yun download` 项目依赖于这些优秀的库：

- `niquests`- 网络请求。
- `aiofiles`- 异步文件读写。
- `rich`-命令行进度条。
- `certifi`-SSL 证书。
- `idna`- 国际化域名支持。
- `sniffio`- 异步库自动检测。

## 安装

使用 pip 安装：

```
$ pip install yundownload
```

`Yun download` 需要 `Python 3.10+`