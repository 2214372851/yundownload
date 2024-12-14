def pool_download():
    from yundownload import Request, AsyncDownloadPools, show_log, DownloadPools
    from pathlib import Path
    show_log()
    request = Request(
        url='http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/working/20130718_phase3_samples_cortex_graphs/KHV/HG02127.uncleaned.q10.k31.ctx',
        save_path='./test_tmp/qq.exe',
        slice_threshold=100 * 1024 * 1024,
    )
    with DownloadPools(max_workers=3) as pool:
        pool.push(request)
    # Path('./test_tmp/qq.exe').unlink()
    return request.is_success()


if __name__ == '__main__':
    import asyncio
    pool_download()
