import sys
import time
from typing import Optional, Tuple
from tqdm import tqdm
from threading import Thread
from queue import Queue


class ProgressBar:
    """
    下载进度条显示类
    
    该类用于在终端中显示下载进度条，包括已下载大小、总大小、下载速度和剩余时间等信息。
    """
    
    def __init__(self, total_size: int, desc: str = "Downloading"):
        """
        初始化进度条
        
        Args:
            total_size: 文件总大小（字节）
            desc: 进度条描述文字
        """
        self.total_size = total_size
        self.current_size = 0
        self.desc = desc
        self.start_time = time.time()
        self._queue = Queue()
        self._thread: Optional[Thread] = None
        self._stopped = False
        self._tqdm_bar: Optional[tqdm] = None
    
    def update(self, bytes_downloaded: int) -> None:
        """
        更新下载进度
        
        Args:
            bytes_downloaded: 本次下载的字节数
        """
        self._queue.put(bytes_downloaded)
    
    def _run(self) -> None:
        """
        内部运行方法，用于更新进度条显示
        """
        self._tqdm_bar = tqdm(
            total=self.total_size,
            desc=self.desc,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            dynamic_ncols=True,
            file=sys.stdout
        )
        
        while not self._stopped:
            try:
                bytes_downloaded = self._queue.get(timeout=0.1)
                self.current_size += bytes_downloaded
                self._tqdm_bar.update(bytes_downloaded)
                self._queue.task_done()
            except:
                if self._stopped:
                    break
        
        self._tqdm_bar.close()
    
    def start(self) -> None:
        """启动进度条更新线程"""
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """停止进度条更新线程"""
        self._stopped = True
        if self._thread:
            self._thread.join()
    
    def get_speed(self) -> float:
        """
        获取当前下载速度（字节/秒）
        
        Returns:
            当前下载速度
        """
        elapsed = time.time() - self.start_time
        if elapsed <= 0:
            return 0.0
        return self.current_size / elapsed


class TUIManager:
    """
    TUI管理器，用于管理多个下载任务的进度显示
    """
    
    _instance: Optional['TUIManager'] = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TUIManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self._progress_bars = {}
    
    def add_progress_bar(self, task_id: str, total_size: int, desc: str = "Downloading") -> ProgressBar:
        """
        添加一个新的进度条
        
        Args:
            task_id: 任务ID
            total_size: 文件总大小（字节）
            desc: 进度条描述文字
            
        Returns:
            进度条对象
        """
        progress_bar = ProgressBar(total_size, desc)
        self._progress_bars[task_id] = progress_bar
        return progress_bar
    
    def remove_progress_bar(self, task_id: str) -> None:
        """
        移除一个进度条
        
        Args:
            task_id: 任务ID
        """
        if task_id in self._progress_bars:
            self._progress_bars[task_id].stop()
            del self._progress_bars[task_id]
    
    def get_progress_bar(self, task_id: str) -> Optional[ProgressBar]:
        """
        获取指定任务的进度条
        
        Args:
            task_id: 任务ID
            
        Returns:
            进度条对象（如果存在）
        """
        return self._progress_bars.get(task_id)
    
    def clear(self) -> None:
        """清除所有进度条"""
        for task_id in list(self._progress_bars.keys()):
            self.remove_progress_bar(task_id)