import asyncio
import time
from string import Template
from pathlib import Path
from threading import Thread, Event
from typing import Callable, Union, TypeVar
from yundownload.utils.logger import logger
from random import randint

from yundownload.utils.config import DEFAULT_SLICED_FILE_SUFFIX

T = TypeVar('T')


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
        retry_delay: Union[int, tuple[float, float]] = 2
):
    """
    Retry the decorator

    :param retry_count: Number of retries
    :param retry_delay: Retry interval
    :return:
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            for i in range(retry_count):
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

        return wrapper

    return decorator


def retry_async(retry_count: int = 1, retry_delay: Union[int, tuple[float, float]] = 2):
    """
    Asynchronous retryer

    :param retry_count: Number of retries
    :param retry_delay: Retry interval
    :return:
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        async def wrapper(*args, **kwargs) -> T:
            for i in range(retry_count):
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