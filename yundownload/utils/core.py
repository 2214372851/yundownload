from enum import IntFlag


class Result(IntFlag):
    SUCCESS = 1
    FAILURE = 2
    EXIST = 4
    WAIT = 8
    UNKNOWN = 16

    def is_success(self) -> bool:
        return bool(self & Result.SUCCESS)

    def is_failure(self) -> bool:
        return bool(self & Result.FAILURE)

    def is_exist(self) -> bool:
        return bool(self & Result.EXIST)

    def is_wait(self) -> bool:
        return bool(self & Result.WAIT)

    def __str__(self) -> str:
        return self.name.lower()
