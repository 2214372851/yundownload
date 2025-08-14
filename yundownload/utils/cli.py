from .. import Downloader, Resources
from .. import version
import argparse

def cli():
    parser = argparse.ArgumentParser(
        description="Yun Download"
    )
    parser.add_argument('uri', help="资源链接")
    parser.add_argument('save_path', help="保存路径")
    parser.add_argument('--mc', type=int, default=1, help="最小并发数")
    parser.add_argument('--mx', type=int, default=10, help="最大并发数")
    parser.add_argument('--version', action='version', version=f'YunDownload {version.__version__}', help="显示版本信息并退出")

    args = parser.parse_args()
    with Downloader() as dl:
        resources = Resources(
            uri=args.uri,
            save_path=args.save_path,
            min_concurrency=args.mc,
            max_concurrency=args.mx,
        )
        result = dl.submit(resources).state
        if result.is_failure():
            print(f'file download failed: {args.uri}')
        else:
            print(f'file download success: {args.uri}')

