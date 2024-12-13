def pool_download():
    from yundownload import Request, DownloadPools
    from pathlib import Path
    request = Request(
        url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
        save_path='./test_tmp/qq.exe',
        slice_threshold=100 * 1024 * 1024,
    )
    with DownloadPools(max_workers=3) as pool:
        pool.push(request)
    Path('./test_tmp/qq.exe').unlink()
    return request.is_success()


def test_download():
    assert pool_download()
