import argparse

from . import YunDownloader, Limit
from ._version import __version__


def cli():
    parser = argparse.ArgumentParser(description='Yun Downloader')
    parser.add_argument('url', type=str, help='Download url')
    parser.add_argument('save_path', type=str, help='Save path, including file name')
    parser.add_argument('-mc', '--max_concurrency', default=8, type=int, help='Maximum concurrency')
    parser.add_argument('-mj', '--max_join', type=int, default=16, help='Maximum connection number')
    parser.add_argument('-t', '--timeout', type=int, default=100, help='Timeout period')
    parser.add_argument('-r', '--retry', type=int, default=0, help='Retry times')
    parser.add_argument('--stream', action='store_true', default=False, help='Forced streaming')
    parser.add_argument('--wget', action='store_true', default=False, help='Carry the wget request header')
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}',
                        help='Show the version number and exit')
    parser.set_defaults(help=parser.print_help)

    args = parser.parse_args()
    yun = YunDownloader(
        headers={'User-Agent': 'Wget/1.12 (linux-gnu)'} if args.wget else None,
        limit=Limit(
            max_concurrency=args.max_concurrency,
            max_join=args.max_join,
        ),
        timeout=args.timeout,
        stream=args.stream,
        cli=True
    )
    yun.download(
        url=args.url,
        save_path=args.save_path,
        error_retry=args.retry
    )
