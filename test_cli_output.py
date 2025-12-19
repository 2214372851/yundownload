#!/usr/bin/env python3
"""
Test CLI with better error handling
"""

import subprocess
import sys

def test_cli_with_output():
    """Test CLI and capture output"""
    print("Testing CLI with output capture...")
    
    # Test with log mode
    cmd = [
        sys.executable, "-m", "yundownload.utils.cli",
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "-O", "/tmp/dummy_cli_test.pdf",
        "--log-mode",
        "--timeout", "30"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd="/Users/yunhai/Documents/tests/labels/yundownload_a", 
                              capture_output=True, text=True, timeout=30)
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cli_with_output()