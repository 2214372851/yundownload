import gzip

from yundownload import YunDownloader, Limit
from hashlib import sha256, md5
from pathlib import Path
import logging
from concurrent.futures import ProcessPoolExecutor

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] <%(name)s> [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
    ],
)


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


def main(url: str):
    yun = YunDownloader(
        url=url,
        save_path='brainchromatin/{}'.format(url.split('/')[-1]),
        limit=Limit(
            max_concurrency=8,
            max_join=10
        ),
        headers={'Accept-Encoding': 'identity'},
        retries=100,
        timeout=400,
        stream=True
    )
    # yun.DISTINGUISH_SIZE = 10 * 1024 * 1024
    # yun.CHUNK_SIZE = 10 * 1024 * 1024
    yun.run(error_retry=2)
    # gzip_check(Path('./data/rnacentral_rfam_annotations.tsv.gz'))
    # file2md5(Path('./data/rnacentral_species_specific_ids.fasta.gz'))


if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=6) as executor:
        with open('links.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                executor.submit(main, line.replace('\n', ''))
