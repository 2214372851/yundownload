from yundownload import YunDownloader

import logging

logger = logging.getLogger('yundownload')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s @ %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


yun = YunDownloader(cli=True)

yun.HEARTBEAT_SLEEP = 0.5

yun.download(
    'https://dldir1.qq.com/qqfile/qq/PCQQ9.7.17/QQ9.7.17.29225.exe',
    'qq.exe',
)