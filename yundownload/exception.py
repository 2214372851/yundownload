from pathlib import Path


class FileRangeTransBorderError(Exception):
    """文件范围超出文件大小错误"""

    def __init__(
            self,
            file_path: str | Path,
            correct_size: int,
            message: str = 'The file size is out of bounds',
    ):
        self.message = message
        self.file_path = Path(file_path)
        self.file_size = self.file_path.stat().st_size
        self.correct_size = correct_size
        error_msg = f'{self.file_path.name} Error: {message} | server size {correct_size} not equal local size {self.file_size}'
        super().__init__(error_msg)


class NotSliceSizeError(Exception):
    """没有文件大小的切片下载错误"""

    def __init__(
            self,
            file_path: str | Path,
            message: str = 'The file size is not divisible by the slice size'):
        self.message = message
        self.file_path = Path(file_path)
        error_msg = f'{self.file_path.name} Error: {message}'
        super().__init__(error_msg)
