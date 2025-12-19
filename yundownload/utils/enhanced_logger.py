"""
Enhanced logger that supports both TUI and traditional logging modes
"""

import logging
from typing import TYPE_CHECKING, Optional
import colorlog

if TYPE_CHECKING:
    from ..core import Resources
    from ..utils import Result

from .tui import get_tui


class EnhancedLogger(logging.Logger):
    def __init__(self, name: str = 'download', level: int = logging.INFO):
        super().__init__(name, level)
        self.use_tui = False
        self._tui_task_map = {}  # Map resource to task_id
        
        # Setup traditional logging
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)s - %(name)s(%(process)s) - %(asctime)s - %(message)s%(reset)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        self.addHandler(handler)
    
    def set_tui_mode(self, enabled: bool = True):
        """Enable or disable TUI mode"""
        import os
        # Only enable TUI mode in the main process
        # In multiprocessing, child processes should not update TUI directly
        if enabled:
            # Check if we're in the main process by comparing with the initial process ID
            # or by checking if we're in a ProcessPoolExecutor worker
            try:
                # Try to get the multiprocessing context
                from multiprocessing import current_process
                if current_process().name != 'MainProcess':
                    # We're in a worker process, don't use TUI
                    self.use_tui = False
                    print(f"DEBUG: Disabling TUI in worker process (PID: {os.getpid()}, Process: {current_process().name})")
                else:
                    # We're in the main process
                    self.use_tui = True
                    print(f"DEBUG: TUI mode enabled in main process (PID: {os.getpid()})")
            except Exception as e:
                # Fallback: if we can't determine, assume we're in main process
                self.use_tui = True
                print(f"DEBUG: TUI mode enabled (fallback) in process {os.getpid()}: {e}")
        else:
            self.use_tui = False
            print(f"DEBUG: TUI mode disabled in process {os.getpid()}")
    
    def register_task(self, resources: 'Resources', task_id: str):
        """Register a TUI task for a resource"""
        if self.use_tui:
            resource_key = f"{resources.uri}_{resources.save_path}"
            self._tui_task_map[resource_key] = task_id
    
    def _get_task_id(self, resources: 'Resources') -> Optional[str]:
        """Get TUI task ID for a resource"""
        resource_key = f"{resources.uri}_{resources.save_path}"
        return self._tui_task_map.get(resource_key)
    
    def resource_start(self, resources: 'Resources'):
        """Log resource download start"""
        if self.use_tui:
            task_id = self._get_task_id(resources)
            if task_id:
                tui = get_tui()
                tui.update_task(task_id, status="downloading")
        else:
            self.info(f'🚀Start downloading metadata: {resources.uri} to {resources.save_path}')
    
    def resource_result(self, resources: 'Resources', result: 'Result'):
        """Log resource download result"""
        if self.use_tui:
            task_id = self._get_task_id(resources)
            if task_id:
                tui = get_tui()
                if result.is_failure():
                    error_msg = str(result.error) if hasattr(result, 'error') else "Download failed"
                    tui.update_task(task_id, status="failed", error_message=error_msg)
                else:
                    tui.update_task(task_id, status="completed", progress=1.0)
        else:
            self.info(f'🏁Downloading result: {result} metadata: {resources.uri} to {resources.save_path}')
    
    def resource_error(self, resources: 'Resources', error: Exception):
        """Log resource download error"""
        if self.use_tui:
            task_id = self._get_task_id(resources)
            if task_id:
                tui = get_tui()
                tui.update_task(task_id, status="failed", error_message=str(error))
        else:
            self.error(f'🏗Downloading error: {error} metadata: {resources.uri} to {resources.save_path}', exc_info=True)
    
    def resource_exist(self, resources: 'Resources'):
        """Log resource already exists"""
        if self.use_tui:
            task_id = self._get_task_id(resources)
            if task_id:
                tui = get_tui()
                tui.update_task(task_id, status="completed", progress=1.0)
        else:
            self.info(f'📦Downloading exist: metadata: {resources.uri} to {resources.save_path}')
    
    def resource_log(self, resources: 'Resources', message: str, level: int | str = logging.INFO):
        """Log general resource message"""
        if not self.use_tui:
            self.log(level, f'❓Downloading message: {message} metadata: {resources.uri} to {resources.save_path}')
    
    def resource_p2s(self, resources: 'Resources', progress: float, speed: float, total_size: int = 0):
        """Log progress and speed - the main TUI update method"""
        print(f"DEBUG: resource_p2s called - use_tui={self.use_tui}, progress={progress}, speed={speed}, total_size={total_size}")
        if self.use_tui:
            task_id = self._get_task_id(resources)
            print(f"DEBUG: task_id={task_id}")
            if task_id:
                tui = get_tui()
                
                # Calculate current size based on progress
                current_size = int(total_size * progress) if total_size > 0 else 0
                
                print(f"DEBUG TUI: Updating task {task_id} - progress={progress}, current_size={current_size}, total_size={total_size}, speed={speed}")
                tui.update_task(
                    task_id,
                    total_size=total_size,
                    current_size=current_size,
                    speed=speed,
                    progress=progress,
                    status="downloading"
                )
        else:
            self.info(
                f'📊Downloading progress: {progress} speed: {round(speed / 1024 / 1024, 2)} MB/S '
                f'metadata: {resources.uri} to {resources.save_path}'
            )


# Replace the global logger instance
logger = EnhancedLogger()