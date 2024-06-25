from yundownload import YunDownloader
from hashlib import sha256
from pathlib import Path
import shutil


def file2sha256(path: Path):
    sha = sha256()
    with path.open('rb') as f:
        for byte in iter(lambda: f.read(1024), b""):
            sha.update(byte)
    return sha.hexdigest()


def main():
    shutil.rmtree(Path('./data'))
    yun = YunDownloader(
        url='https://download.jetbrains.com/python/pycharm-professional-242.18071.12.exe?_gl=1*1jivofn*_gcl_au*MTMzMzQzODI4Ni4xNzE5MzI4ODc3*_ga*MjMzNzg3NzIyLjE3MTkzMjg4Nzg.*_ga_9J976DJZ68*MTcxOTMyODg3Ny4xLjEuMTcxOTMyODkzMC43LjAuMA..&_ga=2.186732461.448957342.1719328878-233787722.1719328878',
        save_path='./data/pycharm.exe'
    )
    yun.run()


if __name__ == '__main__':
    main()
