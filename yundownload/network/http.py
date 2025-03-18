import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

import aiofiles
import httpx

from yundownload.network.base import BaseProtocolHandler
from yundownload.utils.config import DEFAULT_HEADERS, DEFAULT_CHUNK_SIZE, DEFAULT_SLICED_CHUNK_SIZE
from yundownload.utils.core import Result
from yundownload.utils.logger import logger
from yundownload.utils.tools import convert_slice_path

if TYPE_CHECKING:
    from yundownload.core.resources import Resources
    from yundownload.utils.equilibrium import DynamicSemaphore


class HttpProtocolHandler(BaseProtocolHandler):

    def __init__(self):
        super().__init__()
        self.client: None | httpx.Client = None
        self.aclient: None | httpx.AsyncClient = None
        self._method = 'GET'
        self._slice_threshold = None

    def download(self, resources: 'Resources'):
        self._slice_threshold = resources.http_slice_threshold
        self._method = resources.http_method

        self.client = httpx.Client(
            timeout=resources.http_timeout,
            auth=resources.http_auth,
            mounts=resources.http_proxy,
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
            transport=httpx.HTTPTransport(
                retries=5
            ),
            verify=resources.http_verify
        )
        self.client.params.merge(resources.http_params)
        self.client.headers.update(resources.http_headers)
        self.client.cookies.update(resources.http_cookies)

        self.aclient = httpx.AsyncClient(
            timeout=resources.http_timeout,
            auth=resources.http_auth,
            mounts=resources.http_proxy,
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
            transport=httpx.AsyncHTTPTransport(
                retries=5
            ),
            verify=resources.http_verify
        )
        return self._match_method(resources)

    @staticmethod
    def check_protocol(uri: str) -> bool:
        check_uri = uri.lower()
        return check_uri.startswith('http') or check_uri.startswith('https')

    def _match_method(self, resources: 'Resources') -> Result:
        try:
            test_response = self.client.head(resources.uri)
            test_response.raise_for_status()
            content_length = int(test_response.headers.get('Content-Length', 0))
            self._total_size = content_length
        except httpx.HTTPStatusError:
            with self.client.stream(self._method, resources.uri, data=resources.http_data) as test_response:
                test_response.raise_for_status()
                content_length = int(test_response.headers.get('Content-Length'))
            test_response = self.client.request(self._method, resources.uri, headers={'Range': 'bytes=0-1'},
                                                data=resources.http_data)
        if resources.save_path.exists():
            if resources.save_path.stat().st_size == content_length:
                return Result.EXIST
            elif resources.save_path.stat().st_size > content_length:
                resources.save_path.unlink()
        resources.save_path.parent.mkdir(parents=True, exist_ok=True)
        breakpoint_flag = self._breakpoint_resumption(test_response)
        resources.metadata['_breakpoint_flag'] = breakpoint_flag
        if breakpoint_flag and content_length > self._slice_threshold:
            logger.info(f'sliced download: {resources.uri} to {resources.save_path}')
            return asyncio.run(self._sliced_download(resources, content_length))
        else:
            logger.info(f'stream download: {resources.uri} to {resources.save_path}')
            return self._stream_download(resources, content_length)

    def _stream_download(self, resources: 'Resources', content_length: int) -> Result:
        headers = {}
        if resources.save_path.exists():
            file_size = resources.save_path.stat().st_size
            if file_size == content_length:
                logger.info(f'file exist skip download: {resources.uri} to {resources.save_path}')
                return Result.EXIST
            elif file_size > content_length:
                resources.save_path.unlink()
            else:
                headers['Range'] = f'bytes={file_size}-'

        with self.client.stream(self._method,
                                resources.uri,
                                headers=headers,
                                data=resources.http_data) as response:
            response.raise_for_status()
            if resources.metadata.get('_breakpoint_flag', False):
                file_mode = 'ab'
            else:
                file_mode = 'wb'
            with resources.save_path.open(file_mode) as f:
                self.current_size += resources.save_path.stat().st_size
                for chunk in response.iter_bytes(chunk_size=DEFAULT_CHUNK_SIZE):
                    f.write(chunk)
                    self.current_size += len(chunk)
        return Result.SUCCESS

    async def _sliced_download(self, resources: 'Resources', content_length: int) -> Result:
        path_template = convert_slice_path(resources.save_path)
        chunks_path = []
        tasks = []
        for start in range(0, content_length, DEFAULT_SLICED_CHUNK_SIZE):
            end = start + DEFAULT_SLICED_CHUNK_SIZE - 1
            if end > content_length:
                end = content_length
            slice_path = path_template(start)
            tasks.append(
                asyncio.create_task(
                    self._sliced_chunked_download(resources, slice_path, start, end, resources.semaphore)
                )
            )
            chunks_path.append(slice_path)
        results = await asyncio.gather(*tasks)
        await self.aclient.aclose()
        if all(results):
            self._merge_chunk(resources.save_path, chunks_path)
            return Result.SUCCESS
        return Result.FAILURE

    async def _sliced_chunked_download(self, resources: 'Resources', save_path: Path, start: int, end: int,
                                       sem: 'DynamicSemaphore') -> bool:
        async with sem:
            logger.info(f'start sliced download: {resources.uri} to {resources.save_path} {start}-{end}')
            headers = {'Range': f'bytes={start}-{end}'}
            if save_path.exists():
                chunk_file_size = save_path.stat().st_size
                if chunk_file_size == DEFAULT_SLICED_CHUNK_SIZE:
                    logger.info(f'slice exist skip download: {resources.uri} to {save_path}')
                    return True
                elif chunk_file_size > DEFAULT_SLICED_CHUNK_SIZE:
                    logger.info(f'slice size is larger than the slice size: {resources.uri} to {save_path}')
                    save_path.unlink()
                elif chunk_file_size == end - start + 1:
                    logger.info(f'slice exist skip download: {resources.uri} to {save_path}')
                    return True
                else:
                    file_start = start + chunk_file_size
                    logger.info(f'slice breakpoint resumption: {resources.uri} to {save_path}')
                    headers['Range'] = f'bytes={file_start}-{end}'
                    if file_start == end:
                        logger.info(f'slice exist skip download: {resources.uri} to {save_path}')
                        return True
            async with self.aclient.stream(self._method,
                                           resources.uri,
                                           headers=headers,
                                           data=resources.http_data) as response:
                response: httpx.Response
                if not response.is_success: sem.record_result(success=False)
                response.raise_for_status()
                async with aiofiles.open(save_path, 'ab') as f:
                    self.current_size += save_path.stat().st_size
                    async for chunk in response.aiter_bytes(chunk_size=DEFAULT_CHUNK_SIZE):
                        await f.write(chunk)
                        self.current_size += len(chunk)
                sem.record_result(response.elapsed.total_seconds(), True)
                await sem.adaptive_update()
            logger.info(f'sliced download success: {resources.uri} to {save_path}')
            return True

    @staticmethod
    def _merge_chunk(save_path: Path, result: list[Path]):
        with save_path.open('wb') as f:
            for chunk_path in result:
                with chunk_path.open('rb') as f_chunk:
                    while True:
                        chunk = f_chunk.read(DEFAULT_CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                logger.info(f'merge chunk success: {save_path} to {chunk_path}')
        for chunk_path in result:
            chunk_path.unlink()
            logger.info(f'delete chunk success: {chunk_path}')
        logger.info(f'merge file success: {save_path}')

    @staticmethod
    def _breakpoint_resumption(response):
        return (response.headers.get('Accept-Ranges') == 'bytes' or
                response.headers.get('Content-Range', '').startswith('bytes 0-1/') or
                response.headers.get('Content-Length') == '2')

    def close(self):
        self.client.close()
