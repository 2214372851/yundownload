import gzip

from yundownload import YunDownloader, Limit
from hashlib import sha256, md5
from pathlib import Path
import logging

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


def main():
    yun = YunDownloader(
        url='https://hgdownload2.soe.ucsc.edu/gbdb/mm9/bbi/wgEncodeCshlLongRnaSeqAdrenalAdult8wksAlnRep2V2.bam',
        save_path='./data/wgEncodeCshlLongRnaSeqAdrenalAdult8wksAlnRep2V2.bam',
        limit=Limit(
            max_concurrency=16,
            max_join=16
        ),
        headers={'Accept-Encoding': 'identity'},
        retries=100,
        timeout=400
        # stream=True
    )
    # yun.DISTINGUISH_SIZE = 10 * 1024 * 1024
    # yun.CHUNK_SIZE = 10 * 1024 * 1024
    yun.run()
    # gzip_check(Path('./data/rnacentral_rfam_annotations.tsv.gz'))
    # file2md5(Path('./data/rnacentral_species_specific_ids.fasta.gz'))


if __name__ == '__main__':
    main()
