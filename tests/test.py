
from yundownload import Downloader, Resources


def test_ftp():
    with Downloader() as d:
        result = d.submit(Resources(
            uri='ftp://yunhai:admin123@192.168.6.99/data/spider_temp/0f03dc87-57ec-4278-bf95-15d4a1ad90d3.zip',
            save_path=r'C:\Users\YUNHAI\Downloads\download-test/test_files/ftp/0f03dc87-57ec-4278-bf95-15d4a1ad90d3.zip'
        ))
        assert result.finish()


def test_http():
    with Downloader() as d:
        result = d.submit(Resources(
            uri="https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe",
            save_path=r"../test_files/http/qq.exe"
        ))
        assert result.finish()


def test_sftp():
    with Downloader() as d:
        result = d.submit(Resources(
            uri='sftp://root:20020308@192.168.6.99/root/quick_start.sh',
            save_path=r'C:\Users\YUNHAI\Downloads\download-test/test_files/sftp/quick_start.sh'
        ))
        assert result.finish()


def test_m3u8():
    with Downloader() as d:
        result = d.submit(Resources(
            uri='https://c1.7bbffvip.com/video/xiantaiyoushu/%E7%AC%AC01%E9%9B%86/index.m3u8',
            save_path=r'C:\Users\YUNHAI\Downloads\download-test/test_files/m3u8/video/download.mp4'
        ))
        assert result.finish()

def test_proxy():
    with Downloader() as d:
        result = d.submit(Resources(
            uri="https://hf-mirror.com/cognitivecomputations/DeepSeek-R1-AWQ/resolve/main/model-00074-of-00074.safetensors?download=true",
            save_path=r"C:\Users\YUNHAI\Downloads\download-test/test_files/http/DeepSeek-R1-AWQ/model-00074-of-00074.safetensors",
            http_proxy={
                'http': 'http://127.0.0.1:7890',
                'https': 'http://127.0.0.1:7890'
            }
        ))
        assert result.finish()