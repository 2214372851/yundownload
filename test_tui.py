#!/usr/bin/env python3
"""
Test script for TUI functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yundownload.utils.tui import get_tui
import time

def test_tui():
    """Test basic TUI functionality"""
    print("Testing TUI functionality...")
    
    # Get TUI instance
    tui = get_tui()
    
    # Start TUI
    tui.start()
    
    try:
        # Add a test task
        task_id = tui.add_task("https://example.com/file.zip", "/tmp/file.zip")
        
        # Simulate download progress
        for i in range(101):
            progress = i / 100.0
            current_size = int(1024 * 1024 * 10 * progress)  # 10MB total
            speed = 1024 * 1024 * 2  # 2MB/s
            
            tui.update_task(
                task_id,
                total_size=1024 * 1024 * 10,  # 10MB
                current_size=current_size,
                speed=speed,
                progress=progress
            )
            
            time.sleep(0.05)  # Small delay to see progress
        
        # Mark as completed
        tui.update_task(task_id, status="completed", progress=1.0)
        
        # Wait a bit to see final state
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        tui.stop()
        print("TUI test completed!")

if __name__ == "__main__":
    test_tui()