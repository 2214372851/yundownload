"""
TUI (Text User Interface) module for displaying download progress
"""

import sys
import os
import time
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class DownloadTask:
    """Represents a single download task"""
    uri: str
    save_path: str
    total_size: int = 0
    current_size: int = 0
    speed: float = 0.0
    progress: float = 0.0
    status: str = "pending"  # pending, downloading, completed, failed, paused
    start_time: Optional[datetime] = None
    eta: Optional[str] = None
    error_message: Optional[str] = None


class TUIProgressDisplay:
    """TUI progress display manager"""
    
    def __init__(self):
        self.tasks: Dict[str, DownloadTask] = {}
        self.display_thread: Optional[threading.Thread] = None
        self.running = False
        self.lock = threading.Lock()
        self.terminal_width = self._get_terminal_width()
        self.last_update = time.time()
        self.update_interval = 0.1  # Update display every 100ms
        
    def _get_terminal_width(self) -> int:
        """Get terminal width, fallback to 80 if not available"""
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except:
            return 80
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        if size == 0:
            return "0 B"
        
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size_float = float(size)
        
        while size_float >= 1024 and unit_index < len(units) - 1:
            size_float /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size_float)} {units[unit_index]}"
        else:
            return f"{size_float:.1f} {units[unit_index]}"
    
    def _format_speed(self, speed: float) -> str:
        """Format download speed"""
        return f"{self._format_size(int(speed))}/s"
    
    def _format_eta(self, task: DownloadTask) -> str:
        """Calculate and format estimated time of arrival"""
        if task.status != "downloading" or task.speed <= 0 or task.total_size <= 0:
            return "--:--"
        
        remaining_bytes = task.total_size - task.current_size
        if remaining_bytes <= 0:
            return "00:00"
        
        remaining_seconds = int(remaining_bytes / task.speed)
        if remaining_seconds < 60:
            return f"00:{remaining_seconds:02d}"
        elif remaining_seconds < 3600:
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
        else:
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
    
    def _create_progress_bar(self, progress: float, width: int = 20) -> str:
        """Create a text-based progress bar"""
        if width <= 0:
            return ""
        
        filled_width = int(width * progress)
        empty_width = width - filled_width
        
        bar = "█" * filled_width + "░" * empty_width
        percentage = f"{int(progress * 100):3d}%"
        
        return f"[{bar}] {percentage}"
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to fit within specified length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _clear_screen(self):
        """Clear terminal screen"""
        if sys.platform.startswith('win'):
            os.system('cls')
        else:
            sys.stdout.write('\033[2J\033[H')
            sys.stdout.flush()
    
    def _move_cursor_to_top(self):
        """Move cursor to top of screen"""
        # Use a simpler approach - just clear and redraw
        self._clear_screen()
    
    def _hide_cursor(self):
        """Hide terminal cursor"""
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
    
    def _show_cursor(self):
        """Show terminal cursor"""
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
    
    def _get_status_color(self, status: str) -> str:
        """Get ANSI color code for status"""
        colors = {
            "pending": "\033[90m",     # Gray
            "downloading": "\033[36m", # Cyan
            "completed": "\033[32m",    # Green
            "failed": "\033[31m",      # Red
            "paused": "\033[33m",      # Yellow
        }
        return colors.get(status, "\033[0m")
    
    def _reset_color(self) -> str:
        """Reset ANSI color"""
        return "\033[0m"
    
    def _render_header(self) -> str:
        """Render TUI header"""
        header = "=" * min(60, self.terminal_width)
        title = "YunDownload - Download Manager"
        title_padding = max(0, (min(60, self.terminal_width) - len(title)) // 2)
        
        return f"{header}\n{' ' * title_padding}{title}\n{header}"
    
    def _render_task(self, task: DownloadTask, index: int) -> str:
        """Render a single task line"""
        # Format components
        filename = self._truncate_text(Path(task.save_path).name, 25)
        progress_bar = self._create_progress_bar(task.progress, 15)
        size_info = f"{self._format_size(task.current_size)}/{self._format_size(task.total_size)}"
        speed_info = self._format_speed(task.speed)
        eta_info = self._format_eta(task)
        
        # Status with color and emoji
        status_emoji = {
            "pending": "⏳",
            "downloading": "↓",
            "completed": "✓",
            "failed": "✗",
            "paused": "⏸"
        }
        status_color = self._get_status_color(task.status)
        status_emoji_char = status_emoji.get(task.status, "?")
        status = f"{status_color}{status_emoji_char}{self._reset_color()}"
        
        # Combine into a single line
        line = f"{index+1:2d}. {filename:<25} {progress_bar} {size_info:<12} {speed_info:<10} {eta_info:<6} {status}"
        
        # Add error message if failed
        if task.status == "failed" and task.error_message:
            line += f"\n    Error: {task.error_message}"
        
        return line
    
    def _render_summary(self) -> str:
        """Render download summary"""
        with self.lock:
            total_tasks = len(self.tasks)
            downloading = sum(1 for task in self.tasks.values() if task.status == "downloading")
            completed = sum(1 for task in self.tasks.values() if task.status == "completed")
            failed = sum(1 for task in self.tasks.values() if task.status == "failed")
            pending = sum(1 for task in self.tasks.values() if task.status == "pending")
        
        total_speed = sum(task.speed for task in self.tasks.values() if task.status == "downloading")
        
        separator = "=" * min(60, self.terminal_width)
        summary = f"{separator}\nSummary: Total: {total_tasks} | ↓: {downloading} | ✓: {completed} | ✗: {failed} | ⏳: {pending} | Speed: {self._format_speed(total_speed)}\n{separator}"
        return summary
    
    def _render_display(self):
        """Render the complete TUI display"""
        if time.time() - self.last_update < self.update_interval:
            return
        
        self.last_update = time.time()
        
        # Clear screen and redraw everything
        self._clear_screen()
        
        # Build complete display
        display_lines = []
        
        # Header
        display_lines.append(self._render_header().strip())
        
        # Tasks
        with self.lock:
            tasks_list = list(self.tasks.values())
        
        for i, task in enumerate(tasks_list):
            display_lines.append(self._render_task(task, i))
        
        # Summary
        display_lines.append(self._render_summary().strip())
        
        # Write all at once
        display_text = "\n".join(display_lines) + "\n"
        sys.stdout.write(display_text)
        sys.stdout.flush()
    
    def _display_loop(self):
        """Main display update loop"""
        while self.running:
            try:
                self._render_display()
                time.sleep(0.05)  # Small sleep to prevent CPU spinning
            except KeyboardInterrupt:
                break
            except Exception as e:
                # Fallback to simple output if TUI fails
                print(f"TUI Error: {e}")
                break
    
    def start(self):
        """Start the TUI display"""
        if self.running:
            return
        
        self.running = True
        self._hide_cursor()
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
    
    def stop(self):
        """Stop the TUI display"""
        if not self.running:
            return
        
        self.running = False
        if self.display_thread:
            self.display_thread.join(timeout=1.0)
        
        self._show_cursor()
        # Clear the screen one final time
        self._clear_screen()
    
    def add_task(self, uri: str, save_path: str) -> str:
        """Add a new download task"""
        task_id = f"{uri}_{save_path}"
        with self.lock:
            self.tasks[task_id] = DownloadTask(
                uri=uri,
                save_path=save_path,
                start_time=datetime.now()
            )
        return task_id
    
    def update_task(self, task_id: str, total_size: int = None, current_size: int = None, 
                   speed: float = None, progress: float = None, status: str = None,
                   error_message: str = None):
        """Update task information"""
        with self.lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            
            # Only update values if they are explicitly provided (not None)
            # This prevents resetting values when only updating status
            if total_size is not None:
                task.total_size = total_size
            if current_size is not None:
                task.current_size = current_size
            if speed is not None:
                task.speed = speed
            if progress is not None:
                task.progress = progress
            if status is not None:
                task.status = status
            if error_message is not None:
                task.error_message = error_message
            
            # Calculate ETA if downloading
            if task.status == "downloading" and task.speed > 0 and task.total_size > 0:
                task.eta = self._format_eta(task)
    
    def remove_task(self, task_id: str):
        """Remove a task from display"""
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
    
    def get_task_status(self, task_id: str) -> Optional[DownloadTask]:
        """Get current task status"""
        with self.lock:
            return self.tasks.get(task_id)


# Global TUI instance
_tui_instance = None

def get_tui() -> TUIProgressDisplay:
    """Get the global TUI instance"""
    global _tui_instance
    if _tui_instance is None:
        _tui_instance = TUIProgressDisplay()
    return _tui_instance