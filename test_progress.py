#!/usr/bin/env python3
"""Test script to debug progress updates"""

import os
import time
from yundownload import Downloader, Resources
from yundownload.utils.enhanced_logger import logger
from yundownload.utils.tui import get_tui
from pathlib import Path
from urllib.parse import urlparse

# Test with a large file to see progress updates
url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
save_path = "test_download.exe"

# Set a shorter interval for testing
os.environ['YUNDOWNLOAD_LOG_EVERY'] = '1'  # Update every 1 second

print("Testing progress updates...")
print(f"LOG_EVERY environment variable: {os.environ.get('YUNDOWNLOAD_LOG_EVERY', 'not set')}")

# Enable TUI mode
tui = get_tui()
tui.start()
logger.set_tui_mode(True)
print(f"TUI mode enabled: {logger.use_tui}")

# Test with TUI mode
try:
    with Downloader() as dl:
        # Set TUI mode
        dl.set_tui_mode(True)
        
        resources = Resources(
            uri=url,
            save_path=save_path,
        )
        
        # Register task with TUI
        task_id = tui.add_task(url, save_path)
        logger.register_task(resources, task_id)
        
        worker_future = dl.submit(resources, task_id)
        # Wait for download to complete
        worker_future.wait()
        result = worker_future.state
        print(f"Download result: {result}")
        
        # Update TUI with final result
        if result.is_failure():
            tui.update_task(task_id, status="failed")
        else:
            tui.update_task(task_id, status="completed", progress=1.0)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    # Stop TUI
    time.sleep(2)  # Let TUI show final state
    tui.stop()

# Clean up
if os.path.exists(save_path):
    os.remove(save_path)