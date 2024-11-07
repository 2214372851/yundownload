import asyncio
import signal
import time
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, wait, Future
from typing import TYPE_CHECKING, Callable, Optional, Awaitable

import httpx
from httpx import Client, AsyncClient

from yundownload.core import Retry, Result, Status, Proxies, Auth
from yundownload.downloader import stream_downloader, slice_downloader, async_stream_downloader, async_slice_downloader
from yundownload.logger import logger

if TYPE_CHECKING:
    from yundownload.request import Request

"""
uvloop 优化协程
"""


class BaseDP:
    _retry: Retry = Retry()
    _future_list = []

    @abstractmethod
    def push(self, item: 'Request'):
        pass

    @abstractmethod
    def _task_fail(self, result: Result):
        pass

    @abstractmethod
    def _task_handle(self, item: 'Request'):
        pass

    @abstractmethod
    def _task_start(self, item: 'Request', func: Callable[[Client | AsyncClient, 'Request'], Result]):
        pass

    @abstractmethod
    def close(self):
        pass


class DownloadPools(BaseDP):

    def __init__(
            self,
            max_workers: int = 5,
            timeout: int = 20,
            retry: Retry = Retry(),
            verify: bool = True,
            proxies: Optional['Proxies'] = None,
            auth: Optional['Auth'] = None,
    ) -> None:
        self._retry = retry
        self._thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_workers)
        self.client = httpx.Client(
            transport=httpx.HTTPTransport(
                retries=self._retry.retry_connect
            ),
            timeout=timeout,
            follow_redirects=True,
            verify=verify,
            mounts=proxies if proxies is None else {
                "http://": httpx.HTTPTransport(proxy=proxies.http),
                "https://": httpx.HTTPTransport(proxy=proxies.https),
            },
            auth=None if auth is None else httpx.BasicAuth(
                username=auth.username,
                password=auth.password
            )
        )

    def _task_start(self, item: 'Request',
                    func: Callable[['Client', 'Request', Callable], Result]) -> Result:
        return func(self.client, item, self._pool_submit)

    def push(self, item: 'Request'):
        future: Future = self._pool_submit(self._task_handle, item)
        self._future_list.append(future)
        pass

    @property
    def _pool_submit(self):
        return self._thread_pool.submit

    def _task_handle(self, item: 'Request') -> Result:
        err = None
        slice_flag = False
        result = None
        for i in range(self._retry.retry):
            try:
                if not slice_flag:
                    item.stat.close()
                    result = self._task_start(item, stream_downloader)
                    if result.status == Status.SLICE:
                        slice_flag = True
                if slice_flag:
                    item.stat.close()
                    result = self._task_start(item, slice_downloader)
                item.status = result.status
                return result
            except Exception as e:
                err = e
                logger.warning(
                    f"retrying... {i} of {self._retry.retry}, error msg: {e} line: {e.__traceback__.tb_lineno}")
                time.sleep(self._retry.retry_delay)
                continue
        result = Result(
            status=Status.FAIL,
            request=item,
            error=err
        )
        self._task_fail(result)
        item.status = result.status
        return result

    def _task_fail(self, result: Result):
        result.request.error_callback(result)

    def results(self):
        return [future.result() for future in self._future_list]

    def close(self):
        wait(self._future_list)
        self._thread_pool.shutdown(wait=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncDownloadPools(BaseDP):

    def __init__(
            self,
            max_workers: int = 5,
            timeout: int = 20,
            retry: Retry = Retry(),
            verify: bool = True,
            proxies: Optional['Proxies'] = None,
            auth: Optional['Auth'] = None,
    ) -> None:
        self._retry = retry
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(max_workers)
        self.client = AsyncClient(
            transport=httpx.AsyncHTTPTransport(
                retries=self._retry.retry_connect
            ),
            timeout=timeout,
            follow_redirects=True,
            verify=verify,
            mounts=proxies if proxies is None else {
                "http://": httpx.AsyncHTTPTransport(proxy=proxies.http),
                "https://": httpx.AsyncHTTPTransport(proxy=proxies.https),
            },
            auth=None if auth is None else httpx.BasicAuth(
                username=auth.username,
                password=auth.password
            )
        )

    async def _task_start(self, item: 'Request',
                          func: Callable[[AsyncClient, 'Request', asyncio.Semaphore], Awaitable[Result]]):
        return await func(self.client, item, self._semaphore)

    async def push(self, item: 'Request'):
        future = asyncio.create_task(self._task_handle(item))
        self._future_list.append(future)

    async def _task_handle(self, item: 'Request') -> Result:
        err = None
        slice_flag = False
        result = None
        for i in range(self._retry.retry):
            try:
                if not slice_flag:
                    item.stat.close()
                    result = await self._task_start(item, async_stream_downloader)
                    if result.status == Status.SLICE:
                        slice_flag = True
                if slice_flag:
                    item.stat.close()
                    result = await self._task_start(item, async_slice_downloader)
                item.status = result.status
                return result
            except Exception as e:
                raise e
                err = e
                logger.warning(
                    f"retrying... {i} of {self._retry.retry}, error msg: {e} line: {e.__traceback__.tb_lineno}")
                time.sleep(self._retry.retry_delay)
                continue
        result = Result(
            status=Status.FAIL,
            request=item,
            error=err
        )
        logger.error(err, exc_info=True)
        await self._task_fail(result)
        item.status = result.status
        return result

    async def _task_fail(self, result: Result):
        await result.request.error_callback(result)

    async def results(self):
        return await asyncio.gather(*self._future_list)

    async def close(self):
        await self.results()
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
