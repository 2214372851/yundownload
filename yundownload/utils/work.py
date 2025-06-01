from concurrent.futures import Future
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from network import BaseProtocolHandler
    from yundownload import Resources, Result


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

    @property
    def finish(self):
        return bool(self._future.result() & (Result.EXIST | Result.SUCCESS))
