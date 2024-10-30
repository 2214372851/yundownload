# from queue import Queue, LifoQueue, SimpleQueue, PriorityQueue
import logging
import time
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, wait, Future
from typing import TYPE_CHECKING, Callable, Optional

import httpx
from httpx import Client

from core import Retry, Result, Status, Proxies, Auth
from downloader import stream_downloader, slice_downloader

if TYPE_CHECKING:
    from yundownload.request import Request

"""
uvloop 优化协程
"""

logger = logging.getLogger(__name__)


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
    def _task_start(self, item: 'Request', func: Callable[['Client', 'Request'], Result]):
        pass

    @abstractmethod
    def close(self):
        pass

    def __del__(self):
        self.close()


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
            proxies=proxies if proxies is None else {
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
                    result = self._task_start(item, stream_downloader)
                    if result.status == Status.SLICE:
                        slice_flag = True
                if slice_flag:
                    result = self._task_start(item, slice_downloader)
                return result
            except Exception as e:
                err = e
                logger.warning(f"An error has occurred, retrying, {i} of {self._retry.retry}, error information: {e}")
                time.sleep(self._retry.retry_delay)
                continue
        result = Result(
            status=Status.FAIL,
            request=item,
            error=err
        )
        self._task_fail(result)
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


class AsyncDownloadPools(DownloadPools):
    pass