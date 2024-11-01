import asyncio
import threading
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from yundownload.request import Request


class Stat:
    def __init__(self, request: 'Request'):
        self._request = request
        self._start_time = time.time()
        self._end_time = None
        self._download_size = 0
        self._last_size = 0
        self._last_time = time.time()
        self._lock = threading.Lock()
        self._alock = asyncio.Lock()

    def close(self):
        self._end_time = time.time()

    def push(self, download_size):
        with self._lock:
            self._download_size += download_size

    async def apush(self, download_size):
        async with self._alock:
            self._download_size += download_size

    def clear(self):
        self._download_size = 0

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def percentage(self):
        if self._request.correct_size is None:
            return 0
        return round(self._download_size / self._request.correct_size, 2)

    @property
    def speed(self):
        now_time = int(time.time())
        speed = (self._download_size - self._last_size) / (now_time - self._last_time)
        self._last_size = self._download_size
        self._last_time = now_time
        return speed
