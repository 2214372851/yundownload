import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from yundownload.utils.tools import Interval
from yundownload.utils import Result
from yundownload.utils.logger import logger

if TYPE_CHECKING:
    from yundownload.core import Resources


class BaseProtocolHandler(ABC):
    def __init__(self):
        """
        Protocol processor base class
        """
        self.start_time = time.time()
        self.current_size = 0
        self._total_size = 0
        self._total = 0
        self._steps = 0
        self.resources = None
        self.timer = Interval(5, self._print)

    def _print(self):
        logger.resource_p2s(self.resources, self.progress, self.speed)

    @property
    def progress(self) -> float:
        """
        Get the progress of your download

        If it cannot be determined based on the file size or step progress, 0 will be returned

        :return: Download progress
        """
        if self._total != 0:
            return self._steps / self._total
        if self._total_size != 0:
            return round(self.current_size / self._total_size, 2)
        return 0

    @property
    def speed(self) -> float:
        """
        Get the download speed

        :return: Download speed
        """
        if self.current_size == 0:
            return 0
        return self.current_size / (time.time() - self.start_time)

    @staticmethod
    @abstractmethod
    def check_protocol(uri: str) -> bool:
        """
        Check if the URI is supported by the current protocol

        :param uri: The URI to check
        :return: True if protocol is supported, false otherwise
        """
        pass

    def __call__(self, resources: 'Resources') -> 'Result': # noqa
        """
        Invoke the download method

        :param resources: Resource object
        :return: Result object
        """
        logger.resource_start(resources)
        try:
            self.timer.start()
            self.resources = resources
            result = self.download(resources)
            if result.is_success():
                logger.resource_result(resources, result)
            elif result.is_exist():
                logger.resource_exist(resources)
        except Exception as e:
            result = Result.FAILURE
            logger.resource_error(resources, e)
        finally:
            self.timer.cancel()
            self._print()

        return result

    @abstractmethod
    def download(self, resources: 'Resources') -> 'Result':
        """
        Download resources
        """
        pass

    @abstractmethod
    def close(self):
        """
        Turn off the resource
        """
        pass

    def __del__(self):
        self.close()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
