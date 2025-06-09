#!/usr/bin/env python3
"""
Simple version display script - no dependencies required
"""

# Version information (kept in sync with main script)
__version__ = "2.2.0"
__build_date__ = "2024-06-09"
__git_hash__ = "dev"
__author__ = "Claude Code"
__license__ = "GPL-3.0"

import sys

def print_version_info():
    """Print formatted version information"""
    print(f"TFT-Moonraker Bridge v{__version__}")
    print(f"Build: {__build_date__} ({__git_hash__})")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} on {sys.platform}")

if __name__ == "__main__":
    print_version_info()