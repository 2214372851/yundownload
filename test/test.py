import gzip

from yundownload import YunDownloader, Limit
from hashlib import sha256, md5
from pathlib import Path


def file2sha256(path: Path):
    sha = sha256()
    with path.open('rb') as f:
        for byte in iter(lambda: f.read(1024), b""):
            sha.update(byte)
    return sha.hexdigest()


def file2md5(path: Path):
    _md5 = md5()
    with path.open('rb') as f:
        for byte in iter(lambda: f.read(1024), b""):
            _md5.update(byte)
    print(_md5.hexdigest())
    return _md5.hexdigest()


def gzip_check(filepath: Path):
    try:
        with gzip.open(filepath, 'rb') as f:
            while f.read(1024):
                pass
        print('完整')
        return True
    except Exception as e:
        print('file error', e)
        return False


def main():
    yun = YunDownloader(
        url='https://down.360safe.com/se/360aibrowser1.1.1108.64.exe',
        save_path='./data/360aibrowser1.1.1108.64.exe',
        limit=Limit(
            max_concurrency=8,
            max_join=16
        ),
        stream=False
    )
    yun.DISTINGUISH_SIZE = 10 * 1024 * 1024
    yun.CHUNK_SIZE = 10 * 1024 * 1024
    yun.run()
    gzip_check(Path('./data/rnacentral_rfam_annotations.tsv.gz'))
    # file2md5(Path('./data/rnacentral_species_specific_ids.fasta.gz'))


if __name__ == '__main__':
    main()
