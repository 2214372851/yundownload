import gzip

from yundownload import YunDownloader, Limit
from hashlib import sha256, md5
from pathlib import Path
import shutil


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
    # shutil.rmtree(Path('./data'))
    yun = YunDownloader(
        url='https://ftp.ebi.ac.uk/pub/databases/RNAcentral/releases/24.0/sequences/rnacentral_species_specific_ids.fasta.gz',
        save_path='./data/rnacentral_species_specific_ids.fasta.gz',
        limit=Limit(
            max_concurrency=8,
            max_join=16
        )
    )
    yun.run()
    gzip_check(Path('./data/rnacentral_species_specific_ids.fasta.gz'))


if __name__ == '__main__':
    main()
