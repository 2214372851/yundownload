import asyncio
import os
import platform
import subprocess
import time
from pathlib import Path
from random import randint
from string import Template
from threading import Thread, Event
from typing import Callable, Union, TypeVar, ParamSpec, Awaitable

from ..utils.config import DEFAULT_SLICED_FILE_SUFFIX
from ..utils.logger import logger

T = TypeVar('T')
P = ParamSpec('P')


def convert_slice_path(path: Path) -> Callable[[int], Path]:
    template_path = Template("{}--$slice_id{}".format(
        path.with_name(path.name.replace('.', '-')).absolute(),
        DEFAULT_SLICED_FILE_SUFFIX
    ))

    def render_slice_path(slice_id: int) -> Path:
        return Path(template_path.substitute(slice_id=slice_id))

    return render_slice_path


def retry(
        retry_count: int = 1,
        retry_delay: Union[int, tuple[float, float]] = 2,
        before_retry: Callable[[], None] = None
):
    """
    Retry the decorator

    :param retry_count: Number of retries
    :param retry_delay: Retry interval
    :param before_retry: Optional function to call before each retry
    :return:
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for i in range(retry_count):
                if before_retry:
                    before_retry()
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retry_count - 1:
                        logger.error(f"Retry {i + 1}/{retry_count} times, error: {e}", exc_info=True)
                        raise e
                    logger.warning(f"Retry {i + 1}/{retry_count} times, error: {e}", exc_info=True)
                    if isinstance(retry_delay, tuple):
                        time.sleep(randint(*retry_delay))
                    else:
                        time.sleep(retry_delay)
            raise RuntimeError("Unreachable code")

        return wrapper

    return decorator


def retry_async(
        retry_count: int = 1,
        retry_delay: Union[int, tuple[float, float]] = 2,
        before_retry: Callable[[], Awaitable[None]] = None
):
    """
    Asynchronous retryer

    :param retry_count: Number of retries
    :param retry_delay: Retry interval
    :param before_retry: Optional function to call before each retry
    :return:
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for i in range(retry_count):
                if before_retry:
                    await before_retry()
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if i == retry_count - 1:
                        logger.error(f"Retry Async {i + 1}/{retry_count} times, error: {e}", exc_info=True)
                        raise e
                    logger.warning(f"Retry Async {i + 1}/{retry_count} times, error: {e}", exc_info=True)
                    if isinstance(retry_delay, tuple):
                        await asyncio.sleep(randint(*retry_delay))
                    else:
                        await asyncio.sleep(retry_delay)
            raise RuntimeError("Unreachable code")

        return wrapper

    return decorator


class Interval(Thread):
    """Call a function after a specified number of seconds:

            t = Timer(30.0, f, args=None, kwargs=None)
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting

    """

    def __init__(self, interval, function, args=None, kwargs=None):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)


def get_system_proxy() -> dict:
    """
    获取系统代理配置

    支持 macOS、Windows、Linux 系统
    macOS: 通过 scutil 命令获取系统设置中的代理
    Windows: 通过注册表获取代理设置
    Linux: 优先读取环境变量

    Returns:
        包含 http 和 https 代理的字典，例如:
        {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
        如果没有配置代理，返回空字典
    """
    proxy_config = {}
    system = platform.system()

    try:
        if system == 'Darwin':  # macOS
            proxy_config = _get_macos_proxy()
        elif system == 'Windows':
            proxy_config = _get_windows_proxy()
        else:  # Linux 等其他系统
            proxy_config = _get_env_proxy()
    except Exception as e:
        logger.warning(f"获取系统代理失败: {e}")

    return proxy_config


def _get_macos_proxy() -> dict:
    """
    通过 scutil 命令获取 macOS 系统代理配置

    Returns:
        包含 http 和 https 代理的字典
    """
    proxy_config = {}

    try:
        result = subprocess.run(
            ['scutil', '--proxy'],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout

        enabled = False
        proxy_host = None
        proxy_port = None

        for line in output.split('\n'):
            line = line.strip()

            if 'HTTPEnable' in line and ':' in line:
                value = line.split(':')[-1].strip()
                if value == '1':
                    enabled = True

            if 'HTTPProxy' in line and ':' in line:
                proxy_host = line.split(':')[-1].strip()

            if 'HTTPPort' in line and ':' in line:
                proxy_port = line.split(':')[-1].strip()

            if enabled and proxy_host and proxy_port:
                proxy_config['http'] = f'http://{proxy_host}:{proxy_port}'
                enabled = False
                proxy_host = None
                proxy_port = None

            if 'HTTPSEnable' in line and ':' in line:
                value = line.split(':')[-1].strip()
                if value == '1':
                    enabled = True

            if 'HTTPSProxy' in line and ':' in line:
                proxy_host = line.split(':')[-1].strip()

            if 'HTTPSPort' in line and ':' in line:
                proxy_port = line.split(':')[-1].strip()

            if enabled and proxy_host and proxy_port:
                proxy_config['https'] = f'http://{proxy_host}:{proxy_port}'
                enabled = False
                proxy_host = None
                proxy_port = None

    except Exception:
        pass

    return proxy_config


def _get_windows_proxy() -> dict:
    """
    通过注册表获取 Windows 系统代理配置

    Returns:
        包含 http 和 https 代理的字典
    """
    proxy_config = {}

    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        )

        proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
        if proxy_enable:
            proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")

            if '=' in proxy_server:
                for part in proxy_server.split(';'):
                    if '=' in part:
                        protocol, address = part.split('=', 1)
                        if protocol in ('http', 'https'):
                            proxy_config[protocol] = f'http://{address}'
            else:
                proxy_config['http'] = f'http://{proxy_server}'
                proxy_config['https'] = f'http://{proxy_server}'

        winreg.CloseKey(key)
    except Exception:
        pass

    return proxy_config


def _get_env_proxy() -> dict:
    """
    从环境变量中获取代理配置

    Returns:
        包含 http 和 https 代理的字典
    """
    proxy_config = {}

    http_proxy = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
    https_proxy = os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY')

    if http_proxy:
        proxy_config['http'] = http_proxy
    if https_proxy:
        proxy_config['https'] = https_proxy

    return proxy_config
