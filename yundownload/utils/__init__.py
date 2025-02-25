from yundownload.utils.logger import logger
from yundownload.utils.tools import convert_slice_path, retry, retry_async
from yundownload.utils.exceptions import (
    DownloadException,
    ChunkUnsupportedException,
    NotSupportedProtocolException,
    ConnectionException,
    AuthException
)
from yundownload.utils.config import (
    DEFAULT_HEADERS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_SLICED_CHUNK_SIZE,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRY,
    DEFAULT_RETRY_DELAY,
    DEFAULT_SLICED_FILE_SUFFIX,
)
from yundownload.utils.core import Result
from yundownload.utils.equilibrium import DynamicSemaphore, DynamicConcurrencyController