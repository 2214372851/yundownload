from dataclasses import dataclass
from enum import IntFlag
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


class Status(IntFlag):
    """
    下载状态
    """
    WAIT = 1
    FAIL = 2
    SUCCESS = 4
    SLICE = 8
    EXIST = 16


@dataclass
class Result:
    """
    下载结果
    """
    status: Status
    request: 'Request'
    error: Exception = None
