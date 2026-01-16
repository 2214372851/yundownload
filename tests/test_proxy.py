import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from yundownload.utils.tools import get_system_proxy
from yundownload.core.resources import Resources


def test_get_system_proxy_from_environment():
    """Test that system proxy is read from environment variables"""
    with patch.dict(os.environ, {
        'http_proxy': 'http://proxy.example.com:8080',
        'https_proxy': 'https://proxy.example.com:8443'
    }):
        proxies = get_system_proxy()
        assert proxies == {
            'http': 'http://proxy.example.com:8080',
            'https': 'https://proxy.example.com:8443'
        }


def test_get_system_proxy_uppercase():
    """Test that uppercase proxy environment variables are also read"""
    with patch.dict(os.environ, {
        'HTTP_PROXY': 'http://proxy.example.com:8080',
        'HTTPS_PROXY': 'https://proxy.example.com:8443'
    }):
        proxies = get_system_proxy()
        assert proxies == {
            'http': 'http://proxy.example.com:8080',
            'https': 'https://proxy.example.com:8443'
        }


def test_get_system_proxy_priority_lowercase():
    """Test that lowercase proxy variables take priority over uppercase"""
    with patch.dict(os.environ, {
        'http_proxy': 'http://lowercase.example.com:8080',
        'HTTP_PROXY': 'http://uppercase.example.com:8080',
        'https_proxy': 'https://lowercase.example.com:8443',
        'HTTPS_PROXY': 'https://uppercase.example.com:8443'
    }):
        proxies = get_system_proxy()
        assert proxies == {
            'http': 'http://lowercase.example.com:8080',
            'https': 'https://lowercase.example.com:8443'
        }


def test_get_system_proxy_no_proxy():
    """Test that empty dict is returned when no proxy is set"""
    with patch.dict(os.environ, {}, clear=True):
        proxies = get_system_proxy()
        assert proxies == {}


def test_resources_use_system_proxy():
    """Test that Resources class uses system proxy when no proxy is provided"""
    with patch.dict(os.environ, {
        'http_proxy': 'http://proxy.example.com:8080',
        'https_proxy': 'https://proxy.example.com:8443'
    }):
        resources = Resources(
            uri='http://example.com/file.txt',
            save_path='/tmp/file.txt'
        )
        assert resources.http_proxy == {
            'http': 'http://proxy.example.com:8080',
            'https': 'https://proxy.example.com:8443'
        }


def test_resources_user_proxy_overrides_system():
    """Test that user-provided proxy overrides system proxy"""
    with patch.dict(os.environ, {
        'http_proxy': 'http://system-proxy.example.com:8080',
        'https_proxy': 'https://system-proxy.example.com:8443'
    }):
        user_proxy = {
            'http': 'http://user-proxy.example.com:9090',
            'https': 'https://user-proxy.example.com:9443'
        }
        resources = Resources(
            uri='http://example.com/file.txt',
            save_path='/tmp/file.txt',
            http_proxy=user_proxy
        )
        assert resources.http_proxy == user_proxy


if __name__ == '__main__':
    # Run all tests
    test_get_system_proxy_from_environment()
    print("✓ test_get_system_proxy_from_environment")
    
    test_get_system_proxy_uppercase()
    print("✓ test_get_system_proxy_uppercase")
    
    test_get_system_proxy_priority_lowercase()
    print("✓ test_get_system_proxy_priority_lowercase")
    
    test_get_system_proxy_no_proxy()
    print("✓ test_get_system_proxy_no_proxy")
    
    test_resources_use_system_proxy()
    print("✓ test_resources_use_system_proxy")
    
    test_resources_user_proxy_overrides_system()
    print("✓ test_resources_user_proxy_overrides_system")
    
    print("\nAll tests passed! ✅")