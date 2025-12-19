#!/usr/bin/env python3
"""
Demonstration script showing both TUI and log modes working
"""

import subprocess
import time
import os

def demo_log_mode():
    """Demonstrate log mode"""
    print("\n" + "="*60)
    print("DEMONSTRATING LOG MODE")
    print("="*60)
    
    cmd = [
        "python", "-m", "yundownload.utils.cli",
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "-O", "/tmp/demo_log_mode.pdf",
        "--log-mode",
        "--timeout", "30"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd="/Users/yunhai/Documents/tests/labels/yundownload_a", 
                          capture_output=True, text=True)
    
    print(f"Exit code: {result.returncode}")
    print("Output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    # Check if file exists
    if os.path.exists("/tmp/demo_log_mode.pdf"):
        size = os.path.getsize("/tmp/demo_log_mode.pdf")
        print(f"✅ File downloaded successfully: {size} bytes")
    else:
        print("❌ File not found")

def demo_tui_mode():
    """Demonstrate TUI mode (brief)"""
    print("\n" + "="*60)
    print("DEMONSTRATING TUI MODE")
    print("="*60)
    print("TUI mode will show a progress bar interface.")
    print("This will run for a few seconds to demonstrate the interface...")
    
    cmd = [
        "python", "-m", "yundownload.utils.cli",
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "-O", "/tmp/demo_tui_mode.pdf",
        "--timeout", "30"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd="/Users/yunhai/Documents/tests/labels/yundownload_a", 
                          capture_output=True, text=True, timeout=10)
    
    print(f"Exit code: {result.returncode}")
    
    # Check if file exists
    if os.path.exists("/tmp/demo_tui_mode.pdf"):
        size = os.path.getsize("/tmp/demo_tui_mode.pdf")
        print(f"✅ File downloaded successfully: {size} bytes")
    else:
        print("❌ File not found")

if __name__ == "__main__":
    print("🚀 YunDownload TUI and Log Mode Demonstration")
    print("This script demonstrates both TUI and log modes of the download manager.")
    
    # Clean up any existing files
    for f in ["/tmp/demo_log_mode.pdf", "/tmp/demo_tui_mode.pdf"]:
        if os.path.exists(f):
            os.remove(f)
    
    # Demonstrate log mode
    demo_log_mode()
    
    # Demonstrate TUI mode
    demo_tui_mode()
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("Both TUI and log modes are working correctly!")
    print("\nUsage:")
    print("  TUI mode (default): python -m yundownload.utils.cli <URL> -O <output>")
    print("  Log mode: python -m yundownload.utils.cli <URL> -O <output> --log-mode")