import argparse

from . import YunDownloader, Limit


def cli():
    parser = argparse.ArgumentParser(description='Yun Downloader')
    parser.add_argument('url', type=str, help='Download url')
    parser.add_argument('save_path', type=str, help='Save path, including file name')
    parser.add_argument('-mc', '--max_concurrency', default=8, type=int, help='Maximum concurrency')
    parser.add_argument('-mj', '--max_join', type=int, default=16, help='Maximum connection number')
    parser.add_argument('-t', '--timeout', type=int, default=100, help='Timeout period')
    parser.add_argument('-r', '--retry', type=int, default=0, help='Retry times')
    parser.add_argument('--stream', action='store_true', default=False, help='Forced streaming')

    args = parser.parse_args()
    yun = YunDownloader(
        url=args.url,
        save_path=args.save_path,
        limit=Limit(
            max_concurrency=args.max_concurrency,
            max_join=args.max_join,
        ),
        timeout=args.timeout,
        stream=args.stream,
        cli=True
    )
    yun.run(error_retry=args.retry)
