from .. import Downloader, Resources
from .. import version
import argparse

def cli():
    parser = argparse.ArgumentParser(
        description="Yun Download"
    )
    parser.add_argument('uri', help="资源链接")
    parser.add_argument('-O', dest='save_path', help="保存路径")
    parser.add_argument('--mc', type=int, default=1, help="最小并发数")
    parser.add_argument('--mx', type=int, default=10, help="最大并发数")
    parser.add_argument('--timeout', type=int, default=10, help="请求超时时间，单位秒")
    parser.add_argument('--version', action='version', version=f'YunDownload {version.__version__}', help="显示版本信息并退出")

    args = parser.parse_args()
    with Downloader() as dl:
        resources = Resources(
            uri=args.uri,
            save_path=args.save_path if args.save_path else args.uri.split('/')[-1],
            min_concurrency=args.mc,
            max_concurrency=args.mx,
            http_timeout=args.timeout,
        )
        result = dl.submit(resources).state
        if result.is_failure():
            print(f'file download failed: {args.uri}')
        else:
            print(f'file download success: {args.uri}')

