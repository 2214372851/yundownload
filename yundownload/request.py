from pathlib import Path
from typing import Literal, TYPE_CHECKING, Optional, Callable
from urllib.parse import urljoin

import httpx

from yundownload.core import Result, Status
from yundownload.logger import logger
from yundownload.stat import Stat

if TYPE_CHECKING:
    from yundownload.core import Auth


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
            slice_size: int = 100 * 1024 * 1024,  # 100M
            auth: Optional['Auth'] = None,
            timeout: int = 20,
            follow_redirects: bool = True,
            stream_size: int = 1024,
            success_callback: Optional[Callable[['Result'], None]] = None,
            error_callback: Optional[Callable[['Result'], None]] = None
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
        self.auth = None if auth is None else httpx.BasicAuth(
            username=auth.username,
            password=auth.password
        )
        # 为 True 时，使用流式下载不采用分片
        self.stream = False
        self.timeout = timeout
        self.follow_redirects = follow_redirects
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
        self.stat.close()
        if self._success_callback is None:
            return
        return self._success_callback(result)

    async def asuccess_callback(self, result: 'Result'):
        self.stat.close()
        if self._success_callback is None:
            return
        return await self._success_callback(result)

    def error_callback(self, result: 'Result'):
        self.stat.close()
        if self._error_callback is None:
            return
        return self._error_callback(result)

    async def aerror_callback(self, result: 'Result'):
        self.stat.close()
        if self._error_callback is None:
            return
        return await self._error_callback(result)

    def join(self, other: str) -> str:
        return urljoin(self.url, other)
