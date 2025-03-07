from yundownload import Downloader, Resources
import argparse

def cli():
    parser = argparse.ArgumentParser(
        description="Yun Download"
    )
    parser.add_argument('uri', help="资源链接")
    parser.add_argument('save_path', help="保存路径")
    args = parser.parse_args()
    with Downloader() as dl:
        resources = Resources(
            uri=args.uri,
            save_path=args.save_path
        )
        result = dl.submit(resources).result()
        if result.is_failure():
            print(f'file download failed: {args.uri}')
        else:
            print(f'file download success: {args.uri}')

