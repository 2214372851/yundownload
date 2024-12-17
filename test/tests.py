async def apool_download():
    from yundownload import Request, AsyncDownloadPools, arender_ui
    from pathlib import Path
    def download():
        print('aaa')
    request = Request(
        url='https://ftp.ncbi.nlm.nih.gov/blast/db/core_nt.58.tar.gz',
        save_path='./test_tmp/core_nt.58.tar.gz',
        slice_threshold=50 * 1024 * 1024,
    )
    request.stream = True
    async with AsyncDownloadPools(max_workers=15) as pool:
        await pool.push(request)
        await arender_ui([request])
    # Path('./test_tmp/deepvariant_callset.zip').unlink()
    return request.is_success()


# def test_download():
# import asyncio
# assert asyncio.run(apool_download())

def stream_download(url, save_path):
    """
    使用流式下载文件。

    参数:
    - url: 文件的网络地址 (字符串)
    - save_path: 文件保存的本地路径 (字符串)
    """
    import requests
    try:
        # 初始化请求，注意加上stream=True来实现流式下载
        response = requests.get(url, stream=True, verify=False)

        # 检查请求是否成功
        if response.status_code == 200:
            # 打开一个文件用于写入
            with open(save_path, 'wb') as file:
                # 分块写入文件
                for chunk in response.iter_content(chunk_size=1024):  # 每次读取1KB数据
                    if chunk:  # 过滤掉保持活动连接的空白数据块
                        file.write(chunk)
                        print(len(chunk))
            print(f"文件下载成功，已保存至：{save_path}")
            return True
        else:
            print(f"下载失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"下载过程中发生错误：{e}")
        return False

def text():
    url = 'https://ftp.ncbi.nlm.nih.gov/blast/db/core_nt.58.tar.gz'
    save_path = './test_tmp/core_nt.58.tar.gz'
    # 下载文件
    stream_download(url, save_path)
text()