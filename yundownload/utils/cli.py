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
        dl.submit(resources)
