async def apool_download():
    from yundownload import Request, AsyncDownloadPools
    from pathlib import Path
    request = Request(
        url='https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
        save_path='./test_tmp/qq.exe',
        slice_threshold=100 * 1024 * 1024,
    )
    async with AsyncDownloadPools(max_workers=3) as pool:
        await pool.push(request)
    Path('./test_tmp/qq.exe').unlink()
    return request.is_success()


def test_download():
    import asyncio
    assert asyncio.run(apool_download())
