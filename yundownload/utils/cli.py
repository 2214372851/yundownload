import argparse
import time
from pathlib import Path
from urllib.parse import urlparse

from .. import Downloader, Resources
from .. import version
from .tui import get_tui
from .enhanced_logger import logger


def cli():
    parser = argparse.ArgumentParser(
        description="Yun Download"
    )
    parser.add_argument('uri', help="资源链接")
    parser.add_argument('-O', dest='save_path', help="保存路径")
    parser.add_argument('--mc', type=int, default=1, help="最小并发数")
    parser.add_argument('--mx', type=int, default=10, help="最大并发数")
    parser.add_argument('--timeout', type=int, default=10, help="请求超时时间，单位秒")
    parser.add_argument('--log-mode', action='store_true', help="使用日志模式显示进度（默认使用TUI界面）")
    parser.add_argument('--version', action='version', version=f'YunDownload {version.__version__}',
                        help="显示版本信息并退出")

    args = parser.parse_args()
    
    # Initialize TUI if not in log mode
    tui = None
    if not args.log_mode:
        tui = get_tui()
        tui.start()
        # Enable TUI mode in logger
        logger.set_tui_mode(True)
    
    try:
        with Downloader() as dl:
            # Set TUI mode if available
            if tui:
                dl.set_tui_mode(True)
            
            resources = Resources(
                uri=args.uri,
                save_path=args.save_path if args.save_path else Path(urlparse(args.uri).path).name,
                min_concurrency=args.mc,
                max_concurrency=args.mx,
                http_timeout=args.timeout,
            )
            
            # Add task to TUI if available
            task_id = None
            if tui:
                task_id = tui.add_task(args.uri, resources.save_path)
                # Register task with logger
                logger.register_task(resources, task_id)
            
            worker_future = dl.submit(resources, task_id)
            # Wait for download to complete
            worker_future.wait()
            result = worker_future.state
            
            # Update TUI with final result
            if tui and task_id:
                if result.is_failure():
                    tui.update_task(task_id, status="failed", error_message=str(result.error) if hasattr(result, 'error') else "Download failed")
                else:
                    tui.update_task(task_id, status="completed", progress=1.0)
            
            # Print final result in log mode
            if args.log_mode:
                if result.is_failure():
                    print(f'file download failed: {args.uri}')
                else:
                    print(f'file download success: {args.uri}')
            
            # Wait a bit in TUI mode to show final status
            if tui:
                time.sleep(1)
                
    finally:
        # Always stop TUI if it was started
        if tui:
            tui.stop()


if __name__ == '__main__':
    cli()
