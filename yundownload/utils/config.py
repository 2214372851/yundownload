import os
from ..utils.core import Environment

DEFAULT_HEADERS = {
    'User-Agent': 'Wget/1.12 (linux-gnu)',
    'Content-Encoding': 'identity',
    'Accept-Encoding': 'identity'
}
DEFAULT_CHUNK_SIZE = int(os.getenv(Environment.DEFAULT_CHUNK_SIZE, 1024 * 1024))
DEFAULT_SLICED_CHUNK_SIZE = int(os.getenv(Environment.DEFAULT_SLICED_CHUNK_SIZE, 100 * 1024 * 1024))
DEFAULT_TIMEOUT = int(os.getenv(Environment.DEFAULT_TIMEOUT, 60))
DEFAULT_MAX_RETRY = int(os.getenv(Environment.DEFAULT_MAX_RETRY, 3))
DEFAULT_RETRY_DELAY = int(os.getenv(Environment.DEFAULT_RETRY_DELAY, 3))
DEFAULT_SLICED_FILE_SUFFIX = '.ydstf'
