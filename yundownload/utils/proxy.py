import os
import platform
from typing import Dict, Optional, Union
from urllib.parse import urlparse

from ..utils.logger import logger


def get_system_proxy() -> Dict[str, Optional[str]]:
    """
    获取系统代理设置
    
    Returns:
        包含http和https代理的字典，如果没有设置则为None
    """
    proxy_config = {
        'http': None,
        'https': None
    }
    
    system = platform.system().lower()
    
    if system == 'windows':
        proxy_config.update(_get_windows_proxy())
    elif system == 'darwin':  # macOS
        proxy_config.update(_get_macos_proxy())
    elif system == 'linux':
        proxy_config.update(_get_linux_proxy())
    
    # 检查环境变量中的代理设置
    env_proxy = _get_env_proxy()
    for key in proxy_config:
        if env_proxy.get(key):
            proxy_config[key] = env_proxy[key]
    
    logger.debug(f"检测到的系统代理配置: {proxy_config}")
    return proxy_config


def _get_windows_proxy() -> Dict[str, Optional[str]]:
    """
    获取Windows系统代理设置
    """
    try:
        import winreg
        proxy_config = {'http': None, 'https': None}
        
        # 打开注册表键
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
            # 检查是否启用代理
            proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
            
            if proxy_enable:
                # 获取代理服务器
                proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
                
                if proxy_server:
                    # 处理代理服务器格式
                    if '=' in proxy_server:
                        # 格式: http=127.0.0.1:8080;https=127.0.0.1:8080
                        for proxy_setting in proxy_server.split(';'):
                            if '=' in proxy_setting:
                                protocol, address = proxy_setting.split('=', 1)
                                if protocol.lower() in ['http', 'https']:
                                    proxy_config[protocol.lower()] = f"http://{address}"
                    else:
                        # 格式: 127.0.0.1:8080 (应用于所有协议)
                        proxy_config['http'] = f"http://{proxy_server}"
                        proxy_config['https'] = f"http://{proxy_server}"
        
        return proxy_config
    except Exception as e:
        logger.warning(f"获取Windows系统代理失败: {e}")
        return {'http': None, 'https': None}


def _get_macos_proxy() -> Dict[str, Optional[str]]:
    """
    获取macOS系统代理设置
    """
    try:
        import subprocess
        proxy_config = {'http': None, 'https': None}
        
        # 获取网络服务名称
        cmd = "networksetup -listnetworkserviceorder | grep 'Hardware Port' | head -1 | cut -d: -f2 | tr -d ' '"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            service_name = result.stdout.strip()
            
            # 检查HTTP代理
            cmd = f"networksetup -getwebproxy '{service_name}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                if "Enabled: Yes" in output:
                    # 提取代理服务器和端口
                    server_line = [line for line in output.split('\n') if 'Server:' in line][0]
                    port_line = [line for line in output.split('\n') if 'Port:' in line][0]
                    
                    server = server_line.split(':')[1].strip()
                    port = port_line.split(':')[1].strip()
                    
                    if server and port:
                        proxy_config['http'] = f"http://{server}:{port}"
            
            # 检查HTTPS代理
            cmd = f"networksetup -getsecurewebproxy '{service_name}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                if "Enabled: Yes" in output:
                    # 提取代理服务器和端口
                    server_line = [line for line in output.split('\n') if 'Server:' in line][0]
                    port_line = [line for line in output.split('\n') if 'Port:' in line][0]
                    
                    server = server_line.split(':')[1].strip()
                    port = port_line.split(':')[1].strip()
                    
                    if server and port:
                        proxy_config['https'] = f"http://{server}:{port}"
        
        return proxy_config
    except Exception as e:
        logger.warning(f"获取macOS系统代理失败: {e}")
        return {'http': None, 'https': None}


def _get_linux_proxy() -> Dict[str, Optional[str]]:
    """
    获取Linux系统代理设置 (主要通过环境变量)
    """
    # Linux系统主要通过环境变量设置代理
    return _get_env_proxy()


def _get_env_proxy() -> Dict[str, Optional[str]]:
    """
    从环境变量获取代理设置
    """
    proxy_config = {'http': None, 'https': None}
    
    # 检查常见的代理环境变量
    env_vars = [
        'HTTP_PROXY', 'http_proxy',
        'HTTPS_PROXY', 'https_proxy',
        'ALL_PROXY', 'all_proxy'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # 根据变量名确定协议类型
            if var.lower() in ['http_proxy', 'http']:
                protocol = 'http'
            elif var.lower() in ['https_proxy', 'https']:
                protocol = 'https'
            else:  # ALL_PROXY
                # ALL_PROXY应用于所有协议
                proxy_config['http'] = value
                proxy_config['https'] = value
                continue
            
            proxy_config[protocol] = value
    
    return proxy_config


def merge_proxy_settings(user_proxy: Optional[Dict[str, str]], 
                        system_proxy: Optional[Dict[str, str]] = None) -> Dict[str, Optional[str]]:
    """
    合并用户设置的代理和系统代理
    
    Args:
        user_proxy: 用户显式设置的代理
        system_proxy: 系统检测到的代理，如果为None则自动获取
        
    Returns:
        合并后的代理配置
    """
    if system_proxy is None:
        system_proxy = get_system_proxy()
    
    # 如果用户显式设置了代理，则使用用户设置
    if user_proxy:
        return user_proxy
    
    # 否则使用系统代理
    return system_proxy


def validate_proxy_url(proxy_url: str) -> bool:
    """
    验证代理URL格式是否正确
    
    Args:
        proxy_url: 代理URL
        
    Returns:
        是否有效
    """
    try:
        parsed = urlparse(proxy_url)
        return parsed.scheme in ['http', 'https', 'socks4', 'socks5'] and bool(parsed.netloc)
    except Exception:
        return False