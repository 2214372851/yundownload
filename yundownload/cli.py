import argparse
import time
from importlib.metadata import version
from typing import Iterator
from typing import List

from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from yundownload.core import Retry, Status
from yundownload.pool import DownloadPools
from yundownload.request import Request
from yundownload.utils import convert_bytes_per_second


def render_ui(requests: List[Request]):
    table = Table(title="Yun Downloader", show_lines=True, expand=True)
    table.add_column("Filename", justify="right", style="cyan", no_wrap=True)
    table.add_column("URI", style="magenta")
    for request in requests:
        table.add_row(request.save_path.name, request.url)

    console = Console()

    with Progress(console=console) as progress:
        for request in requests:
            request.meta['task'] = progress.add_task(f"[red]{request.save_path.name}...", total=1)

        is_ok = False
        while not is_ok:
            console.clear()
            console.print(table)
            speed = 0
            for request in requests:
                percentage = request.stat.percentage
                progress.update(request.meta['task'], completed=percentage)
                speed += request.stat.speed
            console.print(f"[bold green]Speed: {convert_bytes_per_second(speed)}")
            is_ok = all(bool((Status.SUCCESS | Status.FAIL | Status.EXIST) & request.status) for request in requests)
            time.sleep(2.5)


def get_version():
    return version("yundownload")


def load_file(file: str) -> Iterator:
    with open(file, 'r', encoding='utf-8') as f:
        for line in iter(f.readline, ''):
            save_path, url = line.strip().split('<yfd>')
            yield Request(url=url, save_path=save_path)


def cli() -> None:
    parser = argparse.ArgumentParser(description='Yun Downloader')
    subparsers = parser.add_subparsers(dest='subcommand')
    load_parser = subparsers.add_parser('load', help='Load a request')
    load_parser.add_argument('file', type=str, help='yfd file load')
    load_parser.set_defaults(help=load_parser.print_help)

    download = subparsers.add_parser('download', help='Download a file')
    download.add_argument('url', type=str, help='Download url')
    download.add_argument('save_path', type=str, help='Save path, including file name')
    download.add_argument('-mw', '--maxworker', default=8, type=int, help='Maximum concurrency')
    download.add_argument('-t', '--timeout', type=int, default=100, help='Timeout period')
    download.add_argument('-r', '--retry', type=int, default=1, help='Retry times')
    download.add_argument('--stream', action='store_true', default=False, help='Forced streaming')
    download.add_argument('-V', '--version', action='version', version=f'%(prog)s {get_version()}',
                          help='Display version')
    download.set_defaults(help=download.print_help)
    parser.set_defaults(help=parser.print_help)
    args = parser.parse_args()
    if args.subcommand == 'download':
        request = Request(
            url=args.url,
            save_path=args.save_path,
            timeout=args.timeout
        )
        if args.stream:
            request.stream = True
        with DownloadPools(max_workers=args.maxworker, retry=Retry(retry=args.retry)) as pool:
            pool.push(request)
    elif args.subcommand == 'load':
        with DownloadPools() as pool:
            requests = []
            for request in load_file(args.file):
                pool.push(request)
                requests.append(request)
            render_ui(requests)
