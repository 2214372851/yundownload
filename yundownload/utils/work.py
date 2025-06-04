from concurrent.futures import Future
from typing import Type, TYPE_CHECKING
from .core import Result

if TYPE_CHECKING:
    from network import BaseProtocolHandler
    from ..core.resources import Resources


class WorkerFuture:
    def __init__(self, future: Future, protocol: Type['BaseProtocolHandler'], resources: 'Resources'):
        self._future = future
        self._protocol = protocol
        self.resources = resources

    def wait(self):
        self._future.result()

    @property
    def state(self) -> 'Result':
        return self._future.result()

    def finish(self):
        return bool(self._future.result() & (Result.EXIST | Result.SUCCESS))

    def done(self):
        """
        :return: 是否完成
        """
        return self._future.done()

    def cancel(self):
        """
        取消任务
        :return:
        """
        return self._future.cancel()

    def running(self):
        """
        任务是否正在运行
        :return:
        """
        return self._future.running()

    def cancelled(self):
        """
        任务是否被取消
        :return:
        """
        return self._future.cancelled()

    def __repr__(self):
        return f'<WorkerFuture {self._future}>'



