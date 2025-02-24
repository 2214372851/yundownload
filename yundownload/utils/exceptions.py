class DownloadException(Exception):
    """
    Base class for all download exceptions.
    """
    pass


class ChunkUnsupportedException(DownloadException):
    """
    Raised when the download server does not support chunked transfer encoding.
    """
    def __init__(self, uri: str):
        super().__init__(f"Chunked transfer encoding is not supported for URI: {uri}")

class NotSupportedProtocolException(DownloadException):
    """
    Raised when the protocol is not supported.
    """
    def __init__(self, uri: str):
        super().__init__(f"Unable to find specified protocol handler for URI: {uri}")

class ConnectionException(DownloadException):
    """
    Raised when the connection to the server fails.
    """
    def __init__(self, uri: str):
        super().__init__(f"Connection to server failed for URI: {uri}")

class AuthException(DownloadException):
    """
    Raised when the authentication fails.
    """
    def __init__(self, uri: str):
        super().__init__(f"Authentication failed for URI: {uri}")