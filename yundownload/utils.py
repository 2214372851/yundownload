import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING

from httpx import Client

from yundownload.exception import FileRangeTransBorderError

if TYPE_CHECKING:
    from yundownload.request import Request

logger = logging.getLogger(__name__)


def check_range_transborder(
        client: Client,
        request: 'Request'
) -> None:
    try:
        correct_size = get_head_server_size(client, request)
    except:
        correct_size = get_stream_server_size(client, request)
    if correct_size < request.save_path.stat().st_size:
        if request.transborder_delete:
            request.save_path.unlink()
        raise FileRangeTransBorderError(
            file_path=request.save_path,
            correct_size=correct_size,
        )


def get_stream_server_size(
        client: Client,
        request: 'Request'
) -> int:
    with client.stream(
            method=request.method,
            url=request.url,
            params=request.params,
            data=request.data,
            headers=request.headers,
            cookies=request.cookies,
            auth=request.auth,
            timeout=request.timeout,
            follow_redirects=request.follow_redirects,
    ) as response:
        response.raise_for_status()
        return int(response.headers.get('Content-Length', 0))


def get_head_server_size(
        client: Client,
        request: 'Request'
) -> int:
    response = client.head(
        url=request.url,
        params=request.params,
        headers=request.headers,
        cookies=request.cookies,
        auth=request.auth,
        timeout=request.timeout,
        follow_redirects=request.follow_redirects,
    )
    response.raise_for_status()
    return int(response.headers.get('Content-Length'))


def retry(retry_num: int, retry_delay: int):
    def wrapper(func):
        def inner(*args, **kwargs):
            err = None
            for i in range(retry_num):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    err = e
                    logger.warning(f"An error has occurred, retrying, {i} of {retry_num}, error information: {e}")
                    time.sleep(retry_delay)
                    continue
            raise err

        return inner

    return wrapper


def merge_file(slice_flag: str, save_path: Path):
    """
    合并文件
    :param slice_flag: 切片文件标识
    :param save_path: 保存路径
    :return:
    """
    logger.info(f"Start merging files, file path: {save_path}")
    slice_files = list(save_path.parent.glob(f'*{slice_flag}*.ydstf'))
    slice_files.sort(key=lambda x: int(x.stem.split('--')[1]))
    with save_path.open('wb') as wf:
        for file in slice_files:
            logger.info(f'merge chunk: [{file}]')
            with file.open('rb') as rf:
                while True:
                    chunk = rf.read(4096)
                    if not chunk:
                        break
                    wf.write(chunk)

    for file in slice_files:
        file.unlink()
    logger.info(f"Merge file success, file path: {save_path}")
