import asyncio
import time
import platform
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import aiofiles
from httpx import Client, AsyncClient

from yundownload.core import Status
from yundownload.exception import FileRangeTransBorderError
from yundownload.logger import logger

if TYPE_CHECKING:
    from yundownload.request import Request


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


async def async_check_range_transborder(
        client: AsyncClient,
        request: 'Request'
) -> None:
    try:
        correct_size = await async_get_head_server_size(client, request)
    except:
        correct_size = await async_get_stream_server_size(client, request)
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


async def async_get_stream_server_size(
        client: AsyncClient,
        request: 'Request'
) -> int:
    async with client.stream(
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


async def async_get_head_server_size(
        client: AsyncClient,
        request: 'Request'
) -> int:
    response = await client.head(
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


async def async_merge_file(slice_flag: str, save_path: Path):
    """
    合并文件
    :param slice_flag: 切片文件标识
    :param save_path: 保存路径
    :return:
    """
    logger.info(f"Start merging files, file path: {save_path}")
    slice_files = list(save_path.parent.glob(f'*{slice_flag}*.ydstf'))
    slice_files.sort(key=lambda x: int(x.stem.split('--')[1]))
    async with aiofiles.open(save_path, 'wb') as wf:
        for file in slice_files:
            logger.info(f'merge chunk: [{file}]')
            async with aiofiles.open(file, 'rb') as rf:
                while True:
                    chunk = await rf.read(4096)
                    if not chunk:
                        break
                    await wf.write(chunk)
    for file in slice_files:
        file.unlink()
    logger.info(f"Merge file success, file path: {save_path}")


async def async_event_loop_select():
    if platform.system() == 'Windows':
        warnings.warn('Windows system does not support uvloop, use default event loop')
        return
    else:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)


def convert_bytes_per_second(bytes_per_second):
    """将字节数/秒转换为自适应单位"""
    units = ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s']
    index = 0

    while bytes_per_second >= 1024 and index < len(units) - 1:
        bytes_per_second /= 1024.0
        index += 1

    return f"{bytes_per_second:.2f} {units[index]}"


def status_to_str(status: Status):
    return {
        Status.SUCCESS: 'Success',
        Status.FAIL: 'Fail',
        Status.EXIST: 'Exist',
        Status.WAIT: 'Wait',
        Status.SLICE: 'Slice'
    }[status]
