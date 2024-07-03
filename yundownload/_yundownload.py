import asyncio
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from threading import Thread
from typing import Callable

import aiofiles
import httpx
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class Limit:
    max_concurrency: int = 8
    max_join: int = 16


class _DynamicSemaphore:
    def __init__(self, initial_permits):
        self._permits = initial_permits
        self._semaphore = asyncio.Semaphore(initial_permits)
        self._lock = asyncio.Lock()

    async def acquire(self):
        await self._semaphore.acquire()

    def release(self):
        self._semaphore.release()

    async def set_permits(self, permits):
        async with self._lock:
            difference = permits - self._permits
            if difference > 0:
                for _ in range(difference):
                    self._semaphore.release()
            elif difference < 0:
                for _ in range(-difference):
                    await self._semaphore.acquire()
            self._permits = permits

    async def adjust_concurrency(self, concurrency: float, last_concurrency: float):
        slot = self._permits
        if concurrency > last_concurrency:
            slot = max(1, self._permits - 1)
        elif concurrency < last_concurrency:
            slot += 1
        logger.info(f"dynamic concurrency {self._permits}[{last_concurrency}] --> {slot}[{concurrency}]")
        if slot == self._permits: return
        await self.set_permits(slot)

    def get_permits(self):
        return self._permits


class YunDownloader:
    CHUNK_SIZE = 100 * 1024 * 1024
    HEARTBEAT_SLEEP = 5
    DISTINGUISH_SIZE = 500 * 1024 * 1024
    STREAM_SIZE = 1 * 1024 * 1024

    def __init__(self,
                 url: str,
                 save_path: str,
                 limit: Limit = Limit(),
                 dynamic_concurrency: bool = False,
                 update_callable: Callable = None,
                 params: dict = None,
                 auth: httpx.BasicAuth = None,
                 timeout: int = 200,
                 headers: dict = None,
                 cookies: dict = None,
                 stream: bool = False,
                 max_redirects: int = 5,
                 retries: int = 5,
                 verify: bool = True,
                 cli: bool = False):
        self.__update_callable = update_callable
        self.loop: asyncio.AbstractEventLoop | None = None
        self.auth: httpx.BasicAuth | None = auth
        self.limit = limit
        self.tq: tqdm | None = None
        self.cli = cli
        self.retries = retries
        self.verify = verify
        self.max_redirects = max_redirects
        self.semaphore = _DynamicSemaphore(limit.max_concurrency)
        self.url = url
        self.save_path = Path(save_path)
        self.save_path.parent.mkdir(exist_ok=True, parents=True)
        self.timeout = timeout
        self.headers = headers if headers else {}
        self.cookies = cookies
        self.params = params
        self.stream = stream
        self.is_breakpoint = False
        self.content_length = None
        self.download_count = 0
        self.last_count = 0
        self.start_time = time.time()
        self._dynamic_concurrency = dynamic_concurrency
        self._response_time_deque = deque(maxlen=10)
        self._last_concurrency = -1
        self.ping_state = True

    def __check_breakpoint(self):
        with httpx.Client(
                timeout=self.timeout,
                headers=self.headers,
                cookies=self.cookies,
                params=self.params,
                auth=self.auth,
                verify=self.verify,
                transport=httpx.HTTPTransport(retries=self.retries),
                follow_redirects=True) as client:
            try:
                content_res = client.head(self.url, timeout=self.timeout, headers=self.headers, cookies=self.cookies)
                content_res.raise_for_status()
                content_length = int(content_res.headers.get('content-length', -1))
                if content_length == -1: return
                if self.cli:
                    self.tq = tqdm(total=content_length, unit='B', unit_scale=True, desc=self.url.split('/')[-1])
                res = client.get(self.url, headers={'Range': 'bytes=0-1'})
                if res.status_code != 206: return
                self.is_breakpoint = True
                self.content_length = content_length
            except Exception as e:
                logger.error(f'{self.url} check breakpoint error: {e}')

    def __select_downloader(self):
        if self.save_path.exists() and self.save_path.stat().st_size == self.content_length:
            logger.info(f'{self.url} file exists and size correct, skip download')
            if self.cli:
                print(f'\n{self.url} file exists and size correct, skip download')
            return
        self.loop = asyncio.new_event_loop()
        if (not self.stream
                and self.content_length is not None
                and self.content_length > self.DISTINGUISH_SIZE
                and self.is_breakpoint):
            logger.info(f'{self.url} select slice download')
            self.semaphore = _DynamicSemaphore(self.semaphore.get_permits())
            self.ping_state = True
            self.loop.run_until_complete(self.__slice_download())
        else:
            logger.info(f'{self.url} select stream download')
            stop_event = threading.Event()
            t = Thread(target=lambda: self.__heartbeat_t(stop_event), daemon=True)
            t.start()
            self.__stream_download()
            stop_event.set()
            t.join()
        self.loop.close()

    async def __chunk_download(self, client: httpx.AsyncClient, chunk_start: int,
                               chunk_end: int, save_path: Path):
        await self.semaphore.acquire()
        headers = {'Range': f'bytes={chunk_start}-{chunk_end}'}
        if save_path.exists():
            if save_path.stat().st_size == self.CHUNK_SIZE:
                logger.info(f'{save_path} chunk {chunk_start}-{chunk_end} skip')
                self.download_count += self.CHUNK_SIZE
                self.semaphore.release()
                return True
            elif save_path.stat().st_size > self.CHUNK_SIZE:
                save_path.unlink(missing_ok=True)
            else:
                headers['Range'] = f'bytes={chunk_start + save_path.stat().st_size}-{chunk_end}'

        async with client.stream('GET', self.url, headers=headers) as res:
            try:
                res.raise_for_status()
                async with aiofiles.open(save_path, 'ab') as f:
                    async for chunk in res.aiter_bytes(chunk_size=self.STREAM_SIZE):
                        await f.write(chunk)
                        res: httpx.Response
                        self.download_count += len(chunk)
                    self._response_time_deque.append(res.elapsed.seconds)
                return True
            except Exception as e:
                logger.error(f'{save_path} chunk download error: {e}')
                return False
            finally:
                self.semaphore.release()

    async def __slice_download(self):
        # noinspection PyAsyncCall
        ping = self.loop.create_task(self.__heartbeat())

        async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers,
                cookies=self.cookies,
                params=self.params,
                auth=self.auth,
                verify=self.verify,
                transport=httpx.AsyncHTTPTransport(retries=self.retries),
                follow_redirects=True,
                limits=httpx.Limits(max_connections=self.limit.max_join, max_keepalive_connections=self.limit.max_join),
                max_redirects=self.max_redirects) as client:

            tasks = []
            if self.content_length / self.CHUNK_SIZE > 200:
                logger.warning(
                    f'{self.url} The file size exceeds the threshold of 200. Ensure the file server performance')
            for index, chunk_start in enumerate(range(0, self.content_length, self.CHUNK_SIZE)):
                chunk_end = min(chunk_start + self.CHUNK_SIZE - 1, self.content_length)
                save_path = self.save_path.parent / '{}--{}.distributeddownloader'.format(
                    self.save_path.stem, str(index).zfill(5))
                logger.info(f'{self.url} slice download {index} {chunk_start} {chunk_end}')
                tasks.append(self.loop.create_task(
                    self.__chunk_download(client, chunk_start, chunk_end, save_path)))

            tasks = await asyncio.gather(*tasks)
            self.ping_state = False
            await ping
            if all(tasks):
                logger.info(f'{self.save_path} Download all slice success')
                merge_state = await self.__merge_chunk()
                if not merge_state:
                    raise Exception(f'{self.save_path} Merge all slice error')
                logger.info(f'Success download file, run time: {int(time.time() - self.start_time)} S')
            else:
                logger.error(f'{self.save_path} Download all slice error')
                raise Exception(f'{self.save_path} Download all slice error')

    async def __merge_chunk(self):
        slice_files = list(self.save_path.parent.glob(f'*{self.save_path.stem}*.distributeddownloader'))
        slice_files.sort(key=lambda x: int(x.stem.split('--')[1]))

        try:
            with self.save_path.open('wb') as wf:
                # 遍历所有分片文件
                for slice_file in slice_files:
                    # 以二进制读取模式打开分片文件
                    with slice_file.open('rb') as rf:
                        # 不断读取分片文件的内容，直到读取完毕
                        while True:
                            chunk = rf.read(4096)
                            # 如果读取到的块为空，则表示读取完毕，退出循环
                            if not chunk:
                                break
                            # 将读取到的块写入到目标文件中
                            wf.write(chunk)
            for slice_file in slice_files:
                slice_file.unlink()

            logger.info(f'{self.save_path} merge chunk success')
            return True
        except Exception as e:
            logger.error(f'{self.save_path} merge chunk error: {e}')
            return False

    def __stream_download(self):
        with httpx.Client(
                timeout=self.timeout,
                headers=self.headers,
                cookies=self.cookies,
                auth=self.auth,
                verify=self.verify,
                transport=httpx.HTTPTransport(retries=self.retries),
                max_redirects=self.max_redirects) as client:
            headers = {}
            if self.is_breakpoint and self.content_length is not None:
                # 如果保存路径存在，则设置Range请求头，从已下载的大小开始继续下载
                if self.save_path.exists() and self.save_path.stat().st_size < self.content_length:
                    headers['Range'] = f'bytes={self.save_path.stat().st_size}-'
                    self.download_count = self.save_path.stat().st_size
                    logger.info(f'{self.url} breakpoint download')
                elif self.save_path.exists() and self.save_path.stat().st_size == self.content_length:
                    logger.info(f'{self.url} download success')
                    return
                else:
                    self.save_path.unlink(missing_ok=True)
                    logger.info(f'{self.url} new download')
            else:
                self.save_path.unlink(missing_ok=True)
                logger.info(f'{self.url} new download')
            with client.stream('GET', self.url, headers=headers) as res:
                try:
                    res.raise_for_status()
                    with self.save_path.open('ab+') as f:
                        for chunk in res.iter_bytes(chunk_size=self.STREAM_SIZE):
                            f.write(chunk)
                            self.download_count += len(chunk)
                    logger.info(f'{self.save_path} stream download success')
                except Exception as e:
                    logger.error(f'{self.url} stream download error: {e}')
                    raise e

    async def __heartbeat(self):
        while self.ping_state:
            try:
                await asyncio.sleep(self.HEARTBEAT_SLEEP)
                if self.download_count == 0:
                    logger.info(f'{self.url} heartbeat: wait download')
                    continue
                progress = (self.download_count / self.content_length) if self.content_length is not None else -1
                gap = self.download_count - self.last_count
                speed = gap / 1048576 / self.HEARTBEAT_SLEEP
                if self.__update_callable:
                    self.__update_callable(
                        state='PROGRESS',
                        meta={
                            'progress': progress,
                            'speed': speed,
                            'run_time': self.start_time
                        })
                if self.tq:
                    self.tq.update(gap)
                average_concurrency = sum(self._response_time_deque) / len(self._response_time_deque) if len(
                    self._response_time_deque) else None
                logger.info(f'{self.url} '
                            f'heartbeat: {progress * 100:.2f} '
                            f'run_time: {int(time.time() - self.start_time)} '
                            f'speed: {speed:.2f} MB/S '
                            f'response_time: {average_concurrency} '
                            f'download_size: {self.download_count / 1048576:.2f} MB')

                if self._last_concurrency != -1 and self._dynamic_concurrency:
                    await self.semaphore.adjust_concurrency(average_concurrency, self._last_concurrency)
                if average_concurrency is not None:
                    self._last_concurrency = average_concurrency
                self.last_count = self.download_count
            except Exception as e:
                logger.info("Task is cancelling...")
                return

    def __heartbeat_t(self, stop_event):
        while not stop_event.is_set():
            time.sleep(self.HEARTBEAT_SLEEP)
            if self.download_count == 0:
                logger.info(f'{self.url} heartbeat: wait download')
                continue
            progress = (self.download_count / self.content_length) if self.content_length is not None else -1
            gap = self.download_count - self.last_count
            speed = gap / 1048576 / self.HEARTBEAT_SLEEP

            if self.__update_callable:
                self.__update_callable(
                    state='PROGRESS',
                    meta={
                        'progress': progress,
                        'speed': speed,
                        'run_time': self.start_time
                    })
            if self.tq:
                self.tq.update(gap)
            logger.info(f'{self.url} '
                        f'heartbeat: {progress * 100:.2f} '
                        f'run_time: {int(time.time() - self.start_time)} '
                        f'speed: {speed:.2f} MB/S '
                        f'download_size: {self.download_count / 1048576:.2f} MB')

            self.last_count = self.download_count
        logger.info("Task is cancelling...")

    def __workflow(self):
        logger.info(f'{self.url} workflow start')
        self.download_count = 0
        self.__check_breakpoint()
        self.__select_downloader()

    def run(self, error_retry: int | bool = False):
        if isinstance(error_retry, int) and error_retry > 0:
            flag = 0
            while True:
                try:
                    self.__workflow()
                    break
                except Exception as e:
                    logger.error(f'{self.url} download error: {e}')
                    flag += 1
                    if flag >= error_retry:
                        logger.warning(f'{self.url} download retry skip: {e}')
                        raise e
        else:
            self.__workflow()
