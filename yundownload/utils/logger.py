import logging
from typing import TYPE_CHECKING
import colorlog

if TYPE_CHECKING:
    from yundownload.core import Resources
    from yundownload.utils import Result


class Logger(logging.Logger):
    def __init__(self):
        super().__init__('download', level=logging.INFO)
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)s - %(name)s(%(process)s) - %(asctime)s - %(message)s%(reset)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def resource_start(self, resources: 'Resources'):
        self.info(f'🚀Start downloading metadata: {resources.uri} to {resources.save_path}')

    def resource_result(self, resources: 'Resources', result: 'Result'):
        self.info(f'🏁Downloading result: {result} metadata: {resources.uri} to {resources.save_path}')

    def resource_error(self, resources: 'Resources', error: Exception):
        self.error(f'🏗Downloading error: {error} metadata: {resources.uri} to {resources.save_path}', exc_info=True)

    def resource_exist(self, resources: 'Resources'):
        self.info(f'📦Downloading exist: metadata: {resources.uri} to {resources.save_path}')

    def resource_log(self, resources: 'Resources', message: str, lever: int | str = logging.INFO):
        self.log(lever, f'❓Downloading message: {message} metadata: {resources.uri} to {resources.save_path}')

    def resource_p2s(self, resources: 'Resources', progress: float, speed: float):
        self.info(
            f'📊Downloading progress: {progress} speed: {round(speed / 1024 / 1024, 2)} MB/S '
            f'metadata: {resources.uri} to {resources.save_path}')


logger = Logger()
