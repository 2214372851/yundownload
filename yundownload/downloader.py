import logging
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from httpx import Client, Response

from core import Result, Status
from exception import NotSliceSizeError
from utils import check_range_transborder, merge_file

if TYPE_CHECKING:
    from yundownload.request import Request

logger = logging.getLogger(__name__)


def stream_downloader(
        client: Client,
        request: 'Request',
        poll_push: Callable
) -> Result:
    continued_flag = False
    download_size = 0
    request_headers = request.headers.copy()
    if request.save_path.exists():
        request_headers['Range'] = f'bytes={request.save_path.stat().st_size}-'
        download_size = request.save_path.stat().st_size

    with client.stream(
            method=request.method,
            url=request.url,
            params=request.params,
            data=request.data,
            headers=request_headers,
            cookies=request.cookies,
            auth=request.auth,
            timeout=request.timeout,
            follow_redirects=request.follow_redirects,
    ) as response:
        response: Response
        if response.status_code == 416:
            check_range_transborder(
                client,
                request
            )
            logger.info('The file already exists')
            return Result(
                status=Status.EXIST,
                request=request
            )
        response.raise_for_status()
        if response.headers.get('Accept-Ranges', None) == 'bytes':
            continued_flag = True
        correct_size = int(response.headers.get('Content-Length', 0))
        request.save_path.parent.mkdir(exist_ok=True, parents=True)
        if correct_size:
            request.correct_size = correct_size
            if continued_flag and correct_size > request.slice_threshold and not request.stream:
                return Result(
                    status=Status.SLICE,
                    request=request
                )
        with request.save_path.open('ab' if continued_flag else 'wb') as f:
            for chunk in response.iter_bytes(chunk_size=request.stream_size):
                f.write(chunk)
                download_size += len(chunk)

        logger.info(f'{request.save_path.name} file download success')
        result = Result(
            status=Status.SUCCESS,
            request=request
        )
        request.success_callback(result)
        return result


def slice_downloader(
        client: Client,
        request: 'Request',
        poll_push: Callable
) -> Result:
    if not request.correct_size:
        raise NotSliceSizeError
    if request.correct_size / request.slice_size > 100:
        warnings.warn(
            f'{request.save_path.name} if the number of slices in the '
            f'file is too large, check whether the slices are too small')
    slice_flag_name = request.save_path.name.replace('.', '-')
    future_list = []
    for start in range(0, request.correct_size, request.slice_size):
        end = start + request.slice_size - 1
        chunk_path = request.save_path.parent.joinpath(
            '{}--{}.ydstf'.format(
                slice_flag_name,
                start
            )
        )
        future = poll_push(
            chunk_downloader,
            client,
            request,
            start,
            end,
            chunk_path
        )
        future_list.append(future)
    result = [future.result() for future in future_list]
    status = [res[0] for res in result]
    if all(status):
        merge_file(slice_flag_name, request.save_path)
        result = Result(
            status=Status.SUCCESS,
            request=request
        )
        request.success_callback(result)
        return result
    raise list(filter(lambda x: x[1], result))[0]


def chunk_downloader(
        client: Client,
        request: 'Request',
        start: int,
        end: int,
        save_path: Path,
) -> (bool, None | Exception):
    headers = request.headers.copy()
    headers['Range'] = f'bytes={start}-{end}'
    if save_path.exists():
        if save_path.stat().st_size == request.slice_size:
            logger.info('The file chunk already exists skip')
            return True, None
        elif save_path.stat().st_size > request.slice_size:
            save_path.unlink()
        else:
            chunk_start_size = start + save_path.stat().st_size
            headers['Range'] = f'bytes={chunk_start_size}-{end}'
            if chunk_start_size == request.correct_size:
                return True, None
    try:
        with client.stream(
                method=request.method,
                url=request.url,
                params=request.params,
                data=request.data,
                headers=headers,
                cookies=request.cookies,
                auth=request.auth,
                timeout=request.timeout,
                follow_redirects=request.follow_redirects,
        ) as response:
            response: Response
            response.raise_for_status()
            with save_path.open('ab') as f:
                for chunk in response.iter_bytes(chunk_size=request.stream_size):
                    f.write(chunk)
            logger.info(f'{save_path.name} chunk download success')
            return True, None
    except Exception as e:
        logger.error(f'Chunk download error {e}')
        return False, e
