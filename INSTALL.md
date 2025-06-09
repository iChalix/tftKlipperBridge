# TFT-Klipper Bridge Installation Guide

## 📋 Requirements

### System Requirements
- **Python 3.7+** (3.8+ recommended)
- **Linux/Unix system** (Raspberry Pi, Ubuntu, etc.)
- **TFT35 V2** connected via USB/serial
- **Klipper + Moonraker** installed and running

### Python Dependencies
Install using one of these methods:

#### Method 1: Using requirements.txt (Recommended)
```bash
pip3 install --user -r requirements.txt
```

#### Method 2: Individual packages
```bash
pip3 install --user pyserial aiohttp websockets requests
```

#### Method 3: System-wide (requires sudo)
```bash
sudo pip3 install -r requirements.txt
```

## 🚀 Installation Methods

### 1. Interactive Installer (Recommended)
```bash
cd tftKlipperBridge
./install_tft_bridge.sh
```
- Guided setup with prompts
- Auto-detects serial ports
- Creates systemd service
- Comprehensive validation

### 2. Quick Setup
```bash
cd tftKlipperBridge
# Edit configuration at top of script first
./setup_tft_bridge.sh
```
- Edit variables in script
- Minimal interaction
- Fast deployment

### 3. Standalone Mode (Zero Setup)
```bash
cd tftKlipperBridge
./run_standalone.sh
```
- Auto-installs dependencies
- Auto-detects serial port
- No configuration needed
- Perfect for testing

### 4. Manual Installation
```bash
# Install dependencies
pip3 install --user -r requirements.txt

# Copy bridge script
cp tft_moonraker_bridge.py /home/pi/

# Copy Klipper macros
cp klipper_tft_macros.cfg /home/pi/printer_data/config/

# Add to printer.cfg
echo "[include klipper_tft_macros.cfg]" >> /home/pi/printer_data/config/printer.cfg

# Run manually
python3 /home/pi/tft_moonraker_bridge.py --serial-port /dev/ttyUSB0
```

## 🧪 Testing Before Installation

### Safe Test Mode
```bash
# Test with your actual TFT (safe)
./test_bridge.sh

# Test with specific port
./test_bridge.sh /dev/ttyACM0 115200

# Standalone test mode
./run_standalone.sh --test
```

## 🔧 Dependency Details

### Core Dependencies
- **pyserial** (≥3.5) - Serial communication with TFT
- **aiohttp** (≥3.8.0) - Async HTTP for Moonraker API
- **websockets** (≥10.0) - WebSocket support
- **requests** (≥2.25.0) - HTTP fallback support

### Built-in (Python 3.7+)
- asyncio, json, re, argparse, logging
- sys, time, os, signal, dataclasses
- typing, urllib.parse, collections, socket

## 🐍 Python Version Compatibility

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.6 and below | ❌ Not supported | Missing dataclasses |
| 3.7 | ✅ Minimum supported | All features work |
| 3.8+ | ✅ Recommended | Best performance |
| 3.10+ | ✅ Fully tested | Latest features |

## 📦 Package Managers

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3-pip
pip3 install --user -r requirements.txt
```

### Fedora/CentOS
```bash
sudo dnf install python3-pip
pip3 install --user -r requirements.txt
```

### Arch Linux
```bash
sudo pacman -S python-pip
pip3 install --user -r requirements.txt
```

### macOS (for development)
```bash
brew install python3
pip3 install -r requirements.txt
```

## 🔍 Troubleshooting

### "externally-managed-environment" Error
This is a common issue with newer Python installations (Ubuntu 23.04+, Python 3.11+):

```bash
# Solution 1: Use system packages (recommended)
sudo apt update
sudo apt install python3-serial python3-aiohttp python3-websockets python3-requests

# Solution 2: Use virtual environment
python3 -m venv ~/.tft-bridge-venv
source ~/.tft-bridge-venv/bin/activate
pip install -r requirements.txt

# Solution 3: Override restrictions (not recommended)
pip3 install --user --break-system-packages -r requirements.txt
```

### Dependencies Won't Install
```bash
# Try upgrading pip first
python3 -m pip install --upgrade pip

# Install with verbose output
pip3 install --user -v -r requirements.txt

# Check Python version
python3 --version
```

### Permission Issues
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in

# Alternative: Use system packages
sudo apt install python3-serial python3-aiohttp
```

### Missing Development Headers
```bash
# Ubuntu/Debian
sudo apt install python3-dev build-essential

# Fedora/CentOS
sudo dnf install python3-devel gcc
```

## 🆘 Getting Help

1. **Check version compatibility**: `python3 --version`
2. **Verify dependencies**: `pip3 list | grep -E "(serial|aiohttp|websockets|requests)"`
3. **Test installation**: `./version_check.sh info`
4. **Review logs**: Check installation script output
5. **Try standalone mode**: `./run_standalone.sh --test`

## 📝 Next Steps

After successful installation:
1. **Restart Klipper**: `sudo systemctl restart klipper`
2. **Start bridge**: `sudo systemctl start tft-bridge`
3. **Check status**: `sudo systemctl status tft-bridge`
4. **View logs**: `sudo journalctl -u tft-bridge -f`
5. **Test TFT**: Connect TFT and verify functionality

## 🗑️ Uninstallation

To completely remove the TFT bridge from your system:

### Quick Uninstall
```bash
cd tftKlipperBridge
./uninstall_tft_bridge.sh
```

### What Gets Removed
- **Always removed:**
  - TFT bridge systemd service
  - Service configuration files
  - Helper scripts (bridge_control.sh, bridge_status.sh, etc.)
  - Log files

- **Optionally removed** (script will ask):
  - Bridge Python scripts
  - Klipper macro files
  - Virtual environment
  - Include lines from printer.cfg

### Safe Removal
The uninstall script:
- ✅ **Asks before removing optional components**
- ✅ **Creates backups of modified files**
- ✅ **Stops services gracefully**
- ✅ **Verifies complete removal**
- ✅ **Provides removal summary**

### Manual Cleanup (if needed)
```bash
# If uninstall script isn't available
sudo systemctl stop tft-bridge
sudo systemctl disable tft-bridge
sudo rm /etc/systemd/system/tft-bridge.service
sudo systemctl daemon-reload
```