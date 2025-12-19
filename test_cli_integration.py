#!/usr/bin/env python3
"""
Test CLI with TUI functionality
"""

import subprocess
import sys
import time

def test_cli_tui():
    """Test CLI with TUI mode"""
    print("Testing CLI with TUI mode...")
    
    # Test with a small file
    cmd = [
        sys.executable, "-m", "yundownload.utils.cli",
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "-O", "/tmp/dummy_test.pdf",
        "--timeout", "30"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd="/Users/yunhai/Documents/tests/labels/yundownload_a", timeout=60)
        print(f"CLI test completed with exit code: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("CLI test timed out")
    except Exception as e:
        print(f"CLI test failed: {e}")

def test_cli_log_mode():
    """Test CLI with log mode"""
    print("\nTesting CLI with log mode...")
    
    # Test with log mode
    cmd = [
        sys.executable, "-m", "yundownload.utils.cli",
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "-O", "/tmp/dummy_test_log.pdf",
        "--log-mode",
        "--timeout", "30"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd="/Users/yunhai/Documents/tests/labels/yundownload_a", timeout=60)
        print(f"CLI log mode test completed with exit code: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("CLI log mode test timed out")
    except Exception as e:
        print(f"CLI log mode test failed: {e}")

if __name__ == "__main__":
    test_cli_tui()
    test_cli_log_mode()