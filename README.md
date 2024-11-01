[![PyPI version](https://badge.fury.io/py/yundownload.svg)](https://badge.fury.io/py/yundownload)

# Intro

[Official documentation](https://2214372851.github.io/yundownload/)
> This project is a file downloader, supporting dynamic download according to the size of the file to choose the
> download mode, for the connection that supports breakpoint continuation will automatically break the connection, for
> the
> unsupported link will overwrite the previous content, the project includes retry mechanism, etc., currently supports:
> streaming download, large file fragment download.

# Install

`pip install yundownload`

# Document

[yundownload GitHub](https://github.com/2214372851/yundownload)

# Give an example

```python
from yundownload import DownloadPools, Request

with DownloadPools() as pool:
    pool.push(Request(
        url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
        save_path='./1.exe'
    ))
```

## Command line tool

> In version 0.1.16, a command line tool was added, which can be used as follows:

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

fyd文件命令行读取下载（只适用于简单场景）

```shell
$ yundownload load ./test.fyd
```

fyd文件格式

```text
save_path1<fyd>download_url1
save_path2<fyd>download_url2
```

# Update log

- V 0.4.2
    - Fix retry progress
- V 0.4.1
    - Added to file path creation
- V 0.4.0
    - Refactor the core modules, optimize the code structure, and optimize the download speed
- V 0.3.4
    - Fixed event loop duplicate creation
- V 0.3.3
    - Fix progress bar not reset
- V 0.3.2
    - Fixed the file length inconsistency caused by the request header
- V 0.3.1
    - Added version attribute to the package.
      The command line tool wget parameter has also been added to give the request a default header
- V 0.3.0
    - To optimize the performance of the code, need to pay attention to at the same time, in this version and later
      versions of the API changes, details please refer to
      the [official documentation](https://2214372851.github.io/yundownload/) description of V0.3 version
- V 0.2.15
    - Big change, remove 'run' function, add 'download' function. See the documentation.
- V 0.2.14
    - Modified the document and some prompts.
- V 0.2.13
    - Fixed multiple file fragment download file name issue
- V 0.2.12
    - Fixed a size issue with the last piece of the shard download file
- V 0.2.11
    - Removes the compressed portion of the default request header
- V 0.2.10
    - Agent added to support proxy
- V 0.2.9
    - Fix known bugs
- V 0.2.8
    - Fix known bugs and add warnings for subsequent optimization of large file shards
- V 0.2.7
    - Fix known bugs
- V 0.2.6
    - None Example Change the asynchronous writing of files in fragment download
- V 0.2.5
    - Fix known bugs
- V 0.2.4
    - Add the auth parameter to carry identity information
    - You can add the max_redirects parameter to limit the number of redirects
    - Add the retries parameter to specify the number of request tries
    - Add the verify parameter to specify whether to verify the SSL certificate
- V 0.2.3
    - Remove the default log display and add a progress bar to the command line tool
- V 0.2.2
    - Fixed exception handling of sharding download
- V 0.2.1
    - Repair download failure displays complete
- V 0.2.0
    - Fixed an issue with fragment breakpoint continuation in fragment download
- V 0.1.19
    - Fix stream download breakpoint resume issue
- V 0.1.18
    - Fix known bugs
- V 0.1.17
    - Add forced streaming downloads
- V 0.1.16
    - Add command line tools
- V 0.1.15
    - Optimized fragmentation download breakpoint continuation
- V 0.1.14
    - exclude
- V 0.1.13
    - Troubleshooting Heartbeat detection
- V 0.1.12
    - This version throws an exception after a retry failure
- V 0.1.10
    - Optimized breakpoint continuation
    - Optimized concurrent downloads
    - Optimized heartbeat detection
    - Optimized error retry
    - This version still does not throw an exception after a retry failure

# Future

- Provides webui or desktop applications
- Asynchronous support for YunDownloader (although asynchronous is currently used internally, downloader cannot be used
  in asynchronous functions)