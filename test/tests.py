def pool_download():
    from yundownload import Request, DownloadPools, render_ui
    from pathlib import Path
    request = Request(
        url='https://ftp.ebi.ac.uk/empiar/world_availability/10633/data/rawframes/ts_004_037_-57.0.tif',
        save_path='./test_tmp/ts_004_037_-57.0.tif',
        slice_threshold=10 * 1024 * 1024,
    )
    with DownloadPools(max_workers=3) as pool:
        pool.push(request)
        render_ui([request])
    # Path('./test_tmp/qq.exe').unlink()
    return request.is_success()


pool_download()
