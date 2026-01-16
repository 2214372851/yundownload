"""
测试系统代理自动检测功能
"""
import os
from yundownload import Downloader, Resources


def test_system_proxy_detection():
    """
    测试系统代理自动检测功能
    
    该测试验证：
    1. Resources 类能够正确检测系统代理环境变量
    2. 当没有显式设置 http_proxy 参数时，能够自动使用系统代理
    """
    
    # 设置测试代理环境变量
    os.environ['http_proxy'] = 'http://127.0.0.1:7890'
    os.environ['https_proxy'] = 'http://127.0.0.1:7890'
    
    # 创建 Resources 对象，不显式设置 http_proxy
    resources = Resources(
        uri="https://www.google.com",
        save_path="/tmp/test_proxy.html"
    )
    
    # 验证代理配置是否正确
    assert resources.http_proxy.get('http') == 'http://127.0.0.1:7890', \
        f"Expected http proxy 'http://127.0.0.1:7890', got '{resources.http_proxy.get('http')}'"
    assert resources.http_proxy.get('https') == 'http://127.0.0.1:7890', \
        f"Expected https proxy 'http://127.0.0.1:7890', got '{resources.http_proxy.get('https')}'"
    
    print("✓ 系统代理检测测试通过")
    print(f"  - HTTP 代理: {resources.http_proxy.get('http')}")
    print(f"  - HTTPS 代理: {resources.http_proxy.get('https')}")
    
    # 清理环境变量
    del os.environ['http_proxy']
    del os.environ['https_proxy']


def test_explicit_proxy_override():
    """
    测试显式代理设置覆盖系统代理
    
    该测试验证：
    1. 当显式设置 http_proxy 参数时，会覆盖系统代理设置
    """
    
    # 设置系统代理环境变量
    os.environ['http_proxy'] = 'http://127.0.0.1:7890'
    os.environ['https_proxy'] = 'http://127.0.0.1:7890'
    
    # 创建 Resources 对象，显式设置不同的代理
    resources = Resources(
        uri="https://www.google.com",
        save_path="/tmp/test_proxy.html",
        http_proxy={
            'http': 'http://127.0.0.1:8080',
            'https': 'http://127.0.0.1:8080'
        }
    )
    
    # 验证显式设置的代理覆盖了系统代理
    assert resources.http_proxy.get('http') == 'http://127.0.0.1:8080', \
        f"Expected http proxy 'http://127.0.0.1:8080', got '{resources.http_proxy.get('http')}'"
    assert resources.http_proxy.get('https') == 'http://127.0.0.1:8080', \
        f"Expected https proxy 'http://127.0.0.1:8080', got '{resources.http_proxy.get('https')}'"
    
    print("✓ 显式代理覆盖测试通过")
    print(f"  - HTTP 代理: {resources.http_proxy.get('http')}")
    print(f"  - HTTPS 代理: {resources.http_proxy.get('https')}")
    
    # 清理环境变量
    del os.environ['http_proxy']
    del os.environ['https_proxy']


def test_no_system_proxy():
    """
    测试没有系统代理时的行为
    
    该测试验证：
    1. 当系统没有设置代理时，http_proxy 应该为空字典
    """
    
    # 确保没有设置代理环境变量
    if 'http_proxy' in os.environ:
        del os.environ['http_proxy']
    if 'https_proxy' in os.environ:
        del os.environ['https_proxy']
    if 'HTTP_PROXY' in os.environ:
        del os.environ['HTTP_PROXY']
    if 'HTTPS_PROXY' in os.environ:
        del os.environ['HTTPS_PROXY']
    
    # 创建 Resources 对象，不设置代理
    resources = Resources(
        uri="https://www.google.com",
        save_path="/tmp/test_proxy.html"
    )
    
    # 验证代理配置为空
    assert resources.http_proxy == {}, \
        f"Expected empty proxy dict, got '{resources.http_proxy}'"
    
    print("✓ 无系统代理测试通过")
    print(f"  - 代理配置: {resources.http_proxy}")


def test_case_insensitive_proxy_env():
    """
    测试代理环境变量大小写不敏感
    
    该测试验证：
    1. 支持小写环境变量 (http_proxy, https_proxy)
    2. 支持大写环境变量 (HTTP_PROXY, HTTPS_PROXY)
    """
    
    # 清理所有代理环境变量
    for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
        if var in os.environ:
            del os.environ[var]
    
    # 测试小写环境变量
    os.environ['http_proxy'] = 'http://127.0.0.1:7890'
    os.environ['https_proxy'] = 'http://127.0.0.1:7890'
    
    resources = Resources(
        uri="https://www.google.com",
        save_path="/tmp/test_proxy.html"
    )
    
    assert resources.http_proxy.get('http') == 'http://127.0.0.1:7890'
    assert resources.http_proxy.get('https') == 'http://127.0.0.1:7890'
    
    print("✓ 小写环境变量测试通过")
    
    # 清理并测试大写环境变量
    for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
        if var in os.environ:
            del os.environ[var]
    
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
    
    resources = Resources(
        uri="https://www.google.com",
        save_path="/tmp/test_proxy.html"
    )
    
    assert resources.http_proxy.get('http') == 'http://127.0.0.1:7890'
    assert resources.http_proxy.get('https') == 'http://127.0.0.1:7890'
    
    print("✓ 大写环境变量测试通过")
    
    # 清理环境变量
    for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
        if var in os.environ:
            del os.environ[var]


if __name__ == '__main__':
    print("开始测试系统代理自动检测功能...\n")
    
    test_system_proxy_detection()
    print()
    
    test_explicit_proxy_override()
    print()
    
    test_no_system_proxy()
    print()
    
    test_case_insensitive_proxy_env()
    print()
    
    print("所有测试通过！✓")
