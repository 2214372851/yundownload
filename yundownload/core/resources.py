from pathlib import Path
from typing import Union, Literal

from yundownload.utils import DynamicConcurrencyController, DynamicSemaphore


class Resources:
    _set_lock = True

    def __init__(self,
                 uri: str,
                 save_path: Union[str | Path],
                 http_method: Literal['GET', 'POST', 'PUT', 'DELETE'] = 'GET',
                 http_params: dict = None,
                 http_headers: dict = None,
                 http_data: dict = None,
                 http_proxy: dict[str, str] = None,
                 http_cookies: dict = None,
                 http_timeout: int = 30,
                 http_auth: tuple[str, str] = None,
                 http_verify: bool = False,
                 http_slice_threshold: int = 2048 * 1024 * 1024,
                 ftp_timeout: int = 30,
                 ftp_port: int = 21,
                 sftp_port: int = 22,
                 metadata: dict = None,
                 retry: int = 3,
                 retry_delay: int | tuple[int, int] = 10,
                 min_concurrency: int = 1,
                 max_concurrency: int = 30,
                 window_size: int = 100):
        """
        Resource Object

        :param uri: Resource path
        :param save_path: The path where the resource is saved
        :param http_method: HTTP protocol request method
        :param http_params: HTTP request parameters (Valid for M3U8 protocol)
        :param http_headers: HTTP request headers (Valid for M3U8 protocol)
        :param http_data: HTTP request data
        :param http_proxy: HTTP request proxy
        :param http_cookies: HTTP request cookie (Valid for M3U8 protocol)
        :param http_timeout: HTTP request timeout period (Valid for M3U8 protocol)
        :param http_auth: HTTP protocol authentication is requested (Valid for M3U8 protocol)
        :param http_slice_threshold: HTTP protocol sharding threshold
        :param ftp_timeout: FTP request timeout period
        :param ftp_port: FTP protocol request port
        :param sftp_port: SFTP request port
        :param metadata: Custom metadata (for adapting custom protocols)
        :param retry: Number of retries
        :param retry_delay: Retry interval
        :param min_concurrency: Adaptive concurrency minimum
        :param max_concurrency: Adaptive concurrency maximum
        :param window_size: Adaptive concurrency window size
        """
        self.uri = uri
        self.save_path = Path(save_path)

        self.retry = retry
        self.retry_delay = retry_delay
        dcc = DynamicConcurrencyController(min_concurrency, max_concurrency, window_size)
        self.semaphore = DynamicSemaphore(dcc)

        # http protocol and part m3u8 protocol
        self.http_method = http_method
        self.http_params = http_params
        self.http_headers = http_headers
        self.http_data = http_data
        self.http_proxy = http_proxy
        self.http_cookies = http_cookies
        self.http_timeout = http_timeout
        self.http_auth = http_auth
        self.http_verify = http_verify
        self.http_slice_threshold = http_slice_threshold

        self.ftp_timeout = ftp_timeout
        self.ftp_port = ftp_port

        self.sftp_port = sftp_port

        self.metadata = metadata if metadata else {}

    def lock(self):
        """
        Lock the resource object
        """
        self._set_lock = False

    def __setattr__(self, key, value):
        if self._set_lock:
            return super().__setattr__(key, value)
        raise AttributeError(f'{self.__repr__()} it is locked and cannot be modified')

    def __repr__(self):
        return "<Resources {} to {}>".format(self.uri, self.save_path)
