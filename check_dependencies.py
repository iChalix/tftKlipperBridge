#!/usr/bin/env python3
"""
TFT Bridge Dependency Checker
Simple script to check if all required dependencies are installed
"""

import sys
import subprocess

# Required packages mapping
REQUIRED_PACKAGES = {
    'serial': 'pyserial',
    'aiohttp': 'aiohttp', 
    'websockets': 'websockets',
    'requests': 'requests'
}

def check_package(import_name):
    """Check if a package can be imported"""
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def main():
    """Check all dependencies and provide installation guidance"""
    print("TFT Bridge Dependency Checker")
    print("=" * 40)
    
    missing_packages = []
    
    # Check each required package
    for import_name, package_name in REQUIRED_PACKAGES.items():
        if check_package(import_name):
            print(f"✓ {package_name}")
        else:
            print(f"✗ {package_name} (missing)")
            missing_packages.append(package_name)
    
    print()
    
    if not missing_packages:
        print("🎉 All dependencies are installed!")
        return 0
    
    print(f"⚠ Missing {len(missing_packages)} package(s): {', '.join(missing_packages)}")
    print()
    print("To install missing dependencies:")
    print()
    
    # Try to find requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            print("Using requirements.txt (recommended):")
            print("  pip3 install --user -r requirements.txt")
            print()
    except FileNotFoundError:
        pass
    
    print("Or install individually:")
    print(f"  pip3 install --user {' '.join(missing_packages)}")
    print()
    print("System packages (Ubuntu/Debian):")
    system_packages = [f"python3-{pkg.replace('pyserial', 'serial')}" for pkg in missing_packages]
    print(f"  sudo apt install {' '.join(system_packages)}")
    
    return len(missing_packages)

if __name__ == "__main__":
    sys.exit(main())