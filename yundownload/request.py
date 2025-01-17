from pathlib import Path
from typing import Literal, TYPE_CHECKING, Union, Callable, Coroutine, Optional
from urllib.parse import urljoin

from yundownload.core import Result, Status
from yundownload.logger import logger
from yundownload.stat import Stat

if TYPE_CHECKING:
    from yundownload.core import Auth

RequestCallBack = Union[Callable[['Result'], None], Callable[['Result'], Coroutine[None, None, None]], None]


class Request:
    def __init__(
            self,
            url: str,
            save_path: str | Path,
            method: Literal["GET", "POST", "HEAD", "PUT", "DELETE"] = 'GET',
            params: dict = None,
            headers: dict = None,
            cookies: dict = None,
            data: dict = None,
            slice_threshold=500 * 1024 * 1024,  # 500M
            slice_size: int = 50 * 1024 * 1024,  # 50M
            auth: Optional['Auth'] = None,
            timeout: int = 20,
            stream_size: int = 1048576,  # 1M
            success_callback: RequestCallBack = None,
            error_callback: RequestCallBack = None
    ):
        self.url = url
        self.save_path = Path(save_path)
        self.stream_size = stream_size
        self.slice_size = slice_size
        self.correct_size = None
        self.method = method
        self.slice_threshold = slice_threshold
        self.params = params or {}
        self.meta = {}
        self.headers = {
            'User-Agent': 'Wget/1.12 (linux-gnu)',
            'Content-Encoding': 'identity',
            'Accept-Encoding': 'identity'
        }
        if headers is not None:
            self.headers.update(headers)
        self.cookies = cookies or {}
        self.data = data or {}
        self.transborder_delete = False
        self.auth = None if auth is None else (
            auth.username,
            auth.password
        )
        # 为 True 时，使用流式下载不采用分片
        self.stream = False
        self.timeout = timeout
        if callable(success_callback) or success_callback is None:
            self._success_callback = success_callback
        else:
            logger.warning("callback is not callable")
            self._success_callback = None
        if callable(error_callback) or error_callback is None:
            self._error_callback = error_callback
        else:
            logger.warning("callback is not callable")
            self._error_callback = None
        self.stat = Stat(self)
        self.status: Optional[Status] = Status.WAIT

    def success_callback(self, result: 'Result'):
        logger.info(f"[{self.save_path.name}] The task success")
        self.stat.close()
        if self._success_callback is None:
            return
        return self._success_callback(result)

    async def asuccess_callback(self, result: 'Result'):
        logger.info(f"[{self.save_path.name}] The task success")
        self.stat.close()
        if self._success_callback is None:
            return
        return await self._success_callback(result)

    def error_callback(self, result: 'Result'):
        logger.error(f"[{self.save_path.name}] The task failed")
        self.stat.close()
        if self._error_callback is None:
            return
        return self._error_callback(result)

    async def aerror_callback(self, result: 'Result'):
        logger.error(f"[{self.save_path.name}] The task failed")
        self.stat.close()
        if self._error_callback is None:
            return
        return await self._error_callback(result)

    def join(self, other: str) -> str:
        return urljoin(self.url, other)

    def is_done(self) -> bool:
        return (self.status & (Status.SUCCESS | Status.FAIL | Status.EXIST)) != 0

    def is_success(self) -> bool:
        return (self.status & Status.SUCCESS) != 0

    def is_fail(self) -> bool:
        return (self.status & Status.FAIL) != 0

    def __repr__(self) -> str:
        return f"<Request: {self.url}>"
