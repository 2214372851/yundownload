import os
import platform
import subprocess
from pathlib import Path
from typing import Union, Literal, Dict, Optional
from urllib.parse import urlparse

from yundownload.utils import DynamicConcurrencyController, DynamicSemaphore


def _get_proxy_from_env() -> Dict[str, str]:
    """
    从环境变量获取代理设置
    
    支持的环境变量：
    - HTTP_PROXY / http_proxy
    - HTTPS_PROXY / https_proxy
    - ALL_PROXY / all_proxy
    
    Returns:
        包含代理设置的字典
    """
    proxy_dict = {}
    
    # 读取 HTTP 代理（支持大小写）
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    if http_proxy:
        proxy_dict['http'] = http_proxy
    
    # 读取 HTTPS 代理（支持大小写）
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    if https_proxy:
        proxy_dict['https'] = https_proxy
    
    # 读取通用代理（当没有特定协议代理时使用）
    all_proxy = os.environ.get('ALL_PROXY') or os.environ.get('all_proxy')
    if all_proxy:
        if 'http' not in proxy_dict:
            proxy_dict['http'] = all_proxy
        if 'https' not in proxy_dict:
            proxy_dict['https'] = all_proxy
    
    return proxy_dict


def _get_macos_system_proxy() -> Dict[str, str]:
    """
    从 macOS 系统偏好设置获取代理配置
    
    使用 networksetup 命令获取当前网络服务的代理设置
    
    Returns:
        包含代理设置的字典
    """
    proxy_dict = {}
    
    try:
        # 获取当前默认的网络服务（如 Wi-Fi 或 Ethernet）
        result = subprocess.run(
            ['networksetup', '-listallnetworkservices'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return proxy_dict
        
        # 解析网络服务列表，跳过第一行标题
        services = []
        for line in result.stdout.strip().split('\n')[1:]:
            line = line.strip()
            # 跳过以 * 开头的行（表示禁用）
            if line and not line.startswith('*'):
                services.append(line)
        
        # 尝试获取每个服务的代理设置，优先使用有代理配置的服务
        for service in services:
            try:
                # 获取 HTTP 代理
                http_result = subprocess.run(
                    ['networksetup', '-getwebproxy', service],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                
                if http_result.returncode == 0:
                    http_enabled = False
                    http_server = None
                    http_port = None
                    
                    for line in http_result.stdout.strip().split('\n'):
                        if 'Enabled:' in line:
                            http_enabled = 'Yes' in line
                        elif 'Server:' in line:
                            http_server = line.split(':')[1].strip()
                        elif 'Port:' in line:
                            http_port = line.split(':')[1].strip()
                    
                    if http_enabled and http_server and http_port:
                        proxy_dict['http'] = f"http://{http_server}:{http_port}"
                
                # 获取 HTTPS 代理
                https_result = subprocess.run(
                    ['networksetup', '-getsecurewebproxy', service],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                
                if https_result.returncode == 0:
                    https_enabled = False
                    https_server = None
                    https_port = None
                    
                    for line in https_result.stdout.strip().split('\n'):
                        if 'Enabled:' in line:
                            https_enabled = 'Yes' in line
                        elif 'Server:' in line:
                            https_server = line.split(':')[1].strip()
                        elif 'Port:' in line:
                            https_port = line.split(':')[1].strip()
                    
                    if https_enabled and https_server and https_port:
                        proxy_dict['https'] = f"http://{https_server}:{https_port}"
                
                # 如果找到了代理配置，就不再检查其他服务
                if proxy_dict:
                    break
                    
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue
                
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return proxy_dict


def _get_windows_system_proxy() -> Dict[str, str]:
    """
    从 Windows 注册表获取系统代理设置
    
    读取 Internet Settings 中的代理配置
    
    Returns:
        包含代理设置的字典
    """
    proxy_dict = {}
    
    try:
        import winreg
        
        # 打开 Internet Settings 注册表项
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
            0,
            winreg.KEY_READ
        )
        
        # 检查代理是否启用
        try:
            proxy_enable, _ = winreg.QueryValueEx(key, 'ProxyEnable')
            if proxy_enable != 1:
                winreg.CloseKey(key)
                return proxy_dict
        except FileNotFoundError:
            winreg.CloseKey(key)
            return proxy_dict
        
        # 获取代理服务器地址
        try:
            proxy_server, _ = winreg.QueryValueEx(key, 'ProxyServer')
            
            if proxy_server:
                # 解析代理服务器字符串
                # 格式可能是 "http=proxy:port;https=proxy:port" 或 "proxy:port"
                if '=' in proxy_server:
                    # 多协议格式
                    for part in proxy_server.split(';'):
                        if '=' in part:
                            protocol, address = part.split('=', 1)
                            protocol = protocol.strip().lower()
                            if protocol in ('http', 'https'):
                                # 确保地址有协议前缀
                                if not address.startswith('http'):
                                    address = f"http://{address}"
                                proxy_dict[protocol] = address
                else:
                    # 单一代理格式，同时用于 http 和 https
                    if not proxy_server.startswith('http'):
                        proxy_server = f"http://{proxy_server}"
                    proxy_dict['http'] = proxy_server
                    proxy_dict['https'] = proxy_server
                    
        except FileNotFoundError:
            pass
        
        winreg.CloseKey(key)
        
    except ImportError:
        # 非 Windows 平台
        pass
    except (OSError, WindowsError):
        # 注册表访问错误
        pass
    
    return proxy_dict


def _get_linux_system_proxy() -> Dict[str, str]:
    """
    从 Linux 桌面环境获取系统代理设置
    
    支持 GNOME、KDE 等桌面环境的 gsettings 和 kreadconfig5
    
    Returns:
        包含代理设置的字典
    """
    proxy_dict = {}
    
    # 尝试 GNOME/gsettings
    try:
        # 检查是否使用 GNOME 代理
        mode_result = subprocess.run(
            ['gsettings', 'get', 'org.gnome.system.proxy', 'mode'],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        if mode_result.returncode == 0 and 'manual' in mode_result.stdout.lower():
            # 获取 HTTP 代理
            http_host_result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.system.proxy.http', 'host'],
                capture_output=True,
                text=True,
                timeout=3
            )
            http_port_result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.system.proxy.http', 'port'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if http_host_result.returncode == 0 and http_port_result.returncode == 0:
                host = http_host_result.stdout.strip().strip("'")
                port = http_port_result.stdout.strip()
                if host and host != 'none':
                    proxy_dict['http'] = f"http://{host}:{port}"
            
            # 获取 HTTPS 代理
            https_host_result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.system.proxy.https', 'host'],
                capture_output=True,
                text=True,
                timeout=3
            )
            https_port_result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.system.proxy.https', 'port'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if https_host_result.returncode == 0 and https_port_result.returncode == 0:
                host = https_host_result.stdout.strip().strip("'")
                port = https_port_result.stdout.strip()
                if host and host != 'none':
                    proxy_dict['https'] = f"http://{host}:{port}"
            
            # 如果没有特定 HTTPS 代理，使用 HTTP 代理
            if 'http' in proxy_dict and 'https' not in proxy_dict:
                proxy_dict['https'] = proxy_dict['http']
                
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # 如果 gsettings 没有获取到，尝试 KDE/kreadconfig5
    if not proxy_dict:
        try:
            # 获取 HTTP 代理
            http_proxy_result = subprocess.run(
                ['kreadconfig5', '--file', 'kioslaverc', '--group', 'Proxy Settings', '--key', 'httpProxy'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if http_proxy_result.returncode == 0 and http_proxy_result.stdout.strip():
                proxy_url = http_proxy_result.stdout.strip()
                if not proxy_url.startswith('http'):
                    proxy_url = f"http://{proxy_url}"
                proxy_dict['http'] = proxy_url
            
            # 获取 HTTPS 代理
            https_proxy_result = subprocess.run(
                ['kreadconfig5', '--file', 'kioslaverc', '--group', 'Proxy Settings', '--key', 'httpsProxy'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if https_proxy_result.returncode == 0 and https_proxy_result.stdout.strip():
                proxy_url = https_proxy_result.stdout.strip()
                if not proxy_url.startswith('http'):
                    proxy_url = f"http://{proxy_url}"
                proxy_dict['https'] = proxy_url
            elif 'http' in proxy_dict:
                proxy_dict['https'] = proxy_dict['http']
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
    
    return proxy_dict


def _get_system_proxy() -> Dict[str, str]:
    """
    获取系统代理设置
    
    按优先级尝试多种方式获取系统代理：
    1. 环境变量（跨平台通用）
    2. 各平台特定的系统设置
       - Windows: 注册表
       - macOS: networksetup
       - Linux: gsettings / kreadconfig5
    
    Returns:
        包含代理设置的字典，格式为 {'http': 'http://proxy:port', 'https': 'https://proxy:port'}
    """
    # 首先尝试环境变量（优先级最高，用户自定义）
    proxy_dict = _get_proxy_from_env()
    if proxy_dict:
        return proxy_dict
    
    # 根据平台尝试获取系统设置
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        proxy_dict = _get_macos_system_proxy()
    elif system == 'Windows':
        proxy_dict = _get_windows_system_proxy()
    elif system == 'Linux':
        proxy_dict = _get_linux_system_proxy()
    
    return proxy_dict


class Resources:
    _set_lock = True

    def __init__(self,
                 uri: str,
                 save_path: Union[str | Path],
                 http_method: Literal['GET', 'POST', 'PUT', 'DELETE'] = 'GET',
                 http_params: dict = None,
                 http_headers: dict = None,
                 http_data: dict = None,
                 http_proxy: Dict[Literal['http', 'https'], str] = None,
                 http_cookies: dict = None,
                 http_timeout: int = 30,
                 http_auth: tuple[str, str] = None,
                 http_verify: bool = False,
                 http_slice_threshold: int = 2048 * 1024 * 1024,
                 http_sliced_chunk_size: int = 2048 * 1024 * 1024,
                 ftp_timeout: int = 30,
                 ftp_port: int = 21,
                 sftp_port: int = 22,
                 http_stream: bool = False,
                 metadata: dict = None,
                 retry: int = 3,
                 retry_delay: int | tuple[int, int] = 10,
                 min_concurrency: int = 2,
                 max_concurrency: int = 30,
                 window_size: int = 100):
        """
        Resource Object

        :param uri: Resource path
        :param save_path: The path where the resource is saved
        :param http_method: HTTP protocol request method
        :param http_params: HTTP request parameters (Valid for M3U8 protocol)
        :param http_headers: HTTP request headers (Valid for M3U8 protocol)
        :param http_data: HTTP request data
        :param http_proxy: HTTP request proxy { 'http': 'http://xxx', 'https': 'https://xxx' }
        :param http_cookies: HTTP request cookie (Valid for M3U8 protocol)
        :param http_timeout: HTTP request timeout period (Valid for M3U8 protocol)
        :param http_auth: HTTP protocol authentication is requested (Valid for M3U8 protocol)
        :param http_slice_threshold: HTTP protocol sharding threshold
        :param http_sliced_chunk_size: HTTP protocol sharding chunk size
        :param ftp_timeout: FTP request timeout period
        :param ftp_port: FTP protocol request port
        :param sftp_port: SFTP request port
        :param metadata: Custom metadata (for adapting custom protocols)
        :param retry: Number of retries
        :param retry_delay: Retry interval
        :param min_concurrency: Adaptive concurrency minimum
        :param max_concurrency: Adaptive concurrency maximum
        :param window_size: Adaptive concurrency window size
        """
        self.uri = uri
        self.save_path = Path(save_path)

        self.retry = retry
        self.retry_delay = retry_delay
        self.dcc = DynamicConcurrencyController(min_concurrency, max_concurrency, window_size)
        self.semaphore: Optional['DynamicSemaphore'] = None

        # http protocol and part m3u8 protocol
        self.http_stream = http_stream
        self.http_method = http_method
        self.http_params = http_params
        self.http_headers = http_headers
        self.http_data = http_data
        # 如果用户显式设置了代理则使用用户设置，否则自动检测系统代理
        if http_proxy:
            self.http_proxy = http_proxy
        else:
            self.http_proxy = _get_system_proxy()
        self.http_cookies = http_cookies
        self.http_timeout = http_timeout
        self.http_auth = http_auth
        self.http_verify = http_verify
        self.http_slice_threshold = http_slice_threshold
        self.http_sliced_chunk_size = http_sliced_chunk_size

        self.ftp_timeout = ftp_timeout
        self.ftp_port = ftp_port

        self.sftp_port = sftp_port

        self.metadata = metadata if metadata else {}

    def lock(self):
        """
        Lock the resource object
        """
        self._set_lock = False

    def update_semaphore(self):
        self.semaphore = DynamicSemaphore(self.dcc)

    def __setattr__(self, key, value):
        if self._set_lock or key in ('dcc', 'semaphore'):
            return super().__setattr__(key, value)
        raise AttributeError(f'{self.__repr__()} it is locked and cannot be modified')

    def __repr__(self):
        return "<Resources {} to {}>".format(self.uri, self.save_path)
