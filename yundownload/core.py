from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from yundownload.request import Request


@dataclass
class Auth:
    username: str
    password: str


@dataclass
class Proxies:
    http: str
    https: str


@dataclass
class Retry:
    retry: int = 1
    retry_delay: int = 10
    retry_connect: int = 5


class Status(IntEnum):
    """
    下载状态
    """
    FAIL = 0
    SUCCESS = 1
    SLICE = 2
    EXIST = 3


@dataclass
class Result:
    """
    下载结果
    """
    status: Status
    request: 'Request'
    error: Exception = None
