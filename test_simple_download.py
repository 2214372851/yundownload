#!/usr/bin/env python3
"""
Simple test to verify the download functionality works
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yundownload import Downloader, Resources
from yundownload.utils.tui import get_tui
from yundownload.utils.enhanced_logger import logger

def test_simple_download():
    """Test simple download with TUI"""
    print("Testing simple download with TUI...")
    
    # Enable TUI mode
    tui = get_tui()
    tui.start()
    logger.set_tui_mode(True)
    
    try:
        with Downloader() as dl:
            resources = Resources(
                uri="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                save_path="/tmp/dummy_simple.pdf",
                http_timeout=30,
            )
            
            # Add task to TUI
            task_id = tui.add_task(resources.uri, str(resources.save_path))
            logger.register_task(resources, task_id)
            
            print("Starting download...")
            result = dl.submit(resources).state
            
            if result.is_success():
                print("Download completed successfully!")
                tui.update_task(task_id, status="completed", progress=1.0)
            else:
                print(f"Download failed: {result}")
                tui.update_task(task_id, status="failed", error_message=str(result))
            
            # Wait to see final status
            time.sleep(2)
            
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        tui.stop()

if __name__ == "__main__":
    import time
    test_simple_download()