import logging
from logging.handlers import RotatingFileHandler


class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_format = f'[%(asctime)s] [%(levelname)s] >> %(message)s'
        formatter = logging.Formatter(log_format)
        return formatter.format(record)


class CustomHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)


def show_log():
    handler = CustomHandler()
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)


def write_log(log_path: str):
    handler = RotatingFileHandler(log_path, maxBytes=100 * 1024 * 1024, encoding='utf-8')
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)


logger = logging.getLogger('yundownload')
logger.setLevel(logging.INFO)
