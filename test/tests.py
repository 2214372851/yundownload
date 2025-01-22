def pool_download():
    from yundownload import Request, DownloadPools, show_log
    from pathlib import Path
    show_log()
    request = Request(
        url='https://www.encodeproject.org/files/ENCFF900MNG/@@download/ENCFF900MNG.bam',
        save_path='./test_tmp/ENCFF900MNG.bam',
        slice_size=50 * 1024 * 1024,
        slice_threshold=60 * 1024 * 1024,
    )
    with DownloadPools(max_workers=20) as pool:
        pool.push(request)
    # Path('./test_tmp/qq.exe').unlink()
    return request.is_success()

pool_download()
# import asyncio
#
#
# async def apool_download():
#     from yundownload import Request, AsyncDownloadPools, show_log
#     from pathlib import Path
#     show_log()
#     request = Request(
#         url='https://www.encodeproject.org/files/ENCFF900MNG/@@download/ENCFF900MNG.bam',
#         save_path='./test_tmp/ENCFF900MNG.bam',
#         slice_size=50 * 1024 * 1024,
#         slice_threshold=60 * 1024 * 1024,
#     )
#     async with AsyncDownloadPools(max_workers=30) as pool:
#         await pool.push(request)
#     # Path('./test_tmp/qq.exe').unlink()
#     return request.is_success()
#
#
# asyncio.run(apool_download())
