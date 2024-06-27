# Intro

> This project is a file downloader, supporting dynamic download according to the size of the file to choose the
> download mode, for the connection that supports breakpoint continuation will automatically break the connection, for
> the
> unsupported link will overwrite the previous content, the project includes retry mechanism, etc., currently supports:
> streaming download, large file fragment download.

# Install

`pip install yundownload`

# Stash

[yundownload GitHub](https://github.com/2214372851/yundownload)

# Give an example

```python
from yundownload import YunDownloader, Limit

download = YunDownloader(
    url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    limit=Limit(
        max_concurrency=4,
        max_join=4
    ),  # concurrency
    timeout=1000,
    # You are advised to set a longer timeout period for large file fragments because large file fragments exert pressure on the peer server
    dynamic_concurrency=True,
    save_path='QQ9.7.17.29225.exe'
)
# Files larger than this size are downloaded in fragments
download.DISTINGUISH_SIZE = 100 * 1024 * 1024
# The size of each shard at download time
download.CHUNK_SIZE = 100 * 1024 * 1024
# Heartbeat status detection time
download.HEARTBEAT_SLEEP = 1
# Run task. error_retry: Number of retries when an error occurs
download.run(error_retry=3)
```

## Command line tool

> In version 0.1.16, a command line tool was added, which can be used as follows:

```shell
yundownload -h
usage: yundownload [-h] [-mc MAX_CONCURRENCY] [-mj MAX_JOIN] [-t TIMEOUT] [-r RETRY] [--stream] url save_path

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

# Update log
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