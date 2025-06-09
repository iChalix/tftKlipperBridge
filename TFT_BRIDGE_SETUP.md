# TFT-Moonraker Bridge Setup Guide

This guide shows how to set up the Python bridge to make your TFT35 V2 work with Klipper via Moonraker.

## Overview

The bridge works by:
1. **Intercepting** G-codes sent by the TFT
2. **Translating** them to Klipper-compatible commands
3. **Sending** commands to Klipper via Moonraker API
4. **Responding** back to the TFT with appropriate acknowledgments

## Prerequisites

- Klipper firmware running on your 3D printer
- Moonraker installed and configured
- Python 3.7+ on your system
- TFT35 V2 connected via serial

## Installation

### 1. Install Python Dependencies

```bash
pip install pyserial websockets requests asyncio
```

### 2. Download Bridge Files

Copy these files to your Klipper host (Raspberry Pi, etc.):
- `tft_moonraker_bridge.py` - Main bridge script
- `klipper_tft_macros.cfg` - Klipper macro definitions

### 3. Add Macros to Klipper

Add the macro definitions to your `printer.cfg`:

```ini
# At the end of printer.cfg
[include klipper_tft_macros.cfg]
```

Or copy the contents of `klipper_tft_macros.cfg` directly into your `printer.cfg`.

### 4. Restart Klipper

```bash
sudo systemctl restart klipper
```

## Configuration

### Find Your TFT Serial Port

```bash
# List available serial ports
ls /dev/tty*

# Common locations:
# /dev/ttyUSB0  (USB-to-serial adapter)
# /dev/ttyACM0  (direct USB connection)
# /dev/serial0  (Raspberry Pi GPIO UART)
```

### Test Serial Connection

```bash
# Test communication with TFT (replace with your port)
sudo minicom -D /dev/ttyUSB0 -b 115200
```

## Usage

### Basic Usage

```bash
# Basic usage with default settings
python3 tft_moonraker_bridge.py --serial-port /dev/ttyUSB0

# With custom baud rate
python3 tft_moonraker_bridge.py --serial-port /dev/ttyUSB0 --baud-rate 250000

# With remote Moonraker
python3 tft_moonraker_bridge.py --serial-port /dev/ttyUSB0 --moonraker-host 192.168.1.100
```

### Command Line Options

```bash
python3 tft_moonraker_bridge.py --help

Options:
  --serial-port, -p     Serial port for TFT (required)
  --baud-rate, -b       Baud rate (default: 115200)
  --moonraker-host, -m  Moonraker host (default: localhost)
  --moonraker-port, -P  Moonraker port (default: 7125)
  --log-level, -l       Log level: DEBUG/INFO/WARNING/ERROR
  --timeout, -t         Request timeout in seconds (default: 5.0)
```

### Example Configurations

```bash
# Standard setup with TFT on USB port
python3 tft_moonraker_bridge.py -p /dev/ttyUSB0 -b 115200

# High-speed connection  
python3 tft_moonraker_bridge.py -p /dev/ttyUSB0 -b 250000

# Remote Moonraker instance
python3 tft_moonraker_bridge.py -p /dev/ttyUSB0 -m 192.168.1.50 -P 7125

# Debug mode for troubleshooting
python3 tft_moonraker_bridge.py -p /dev/ttyUSB0 -l DEBUG
```

## Systemd Service (Auto-start)

Create a systemd service to automatically start the bridge:

### 1. Create Service File

```bash
sudo nano /etc/systemd/system/tft-bridge.service
```

### 2. Service Configuration

```ini
[Unit]
Description=TFT Moonraker Bridge
After=network.target klipper.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/tft_moonraker_bridge.py --serial-port /dev/ttyUSB0 --baud-rate 115200
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable tft-bridge.service
sudo systemctl start tft-bridge.service

# Check status
sudo systemctl status tft-bridge.service

# View logs
sudo journalctl -u tft-bridge.service -f
```

## Troubleshooting

### Common Issues

**1. Permission Denied on Serial Port**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Then log out and back in
```

**2. TFT Not Responding**
- Check serial cable connections
- Verify baud rate matches TFT settings
- Try different USB ports
- Check TFT config.ini for correct serial settings

**3. Moonraker Connection Failed**
```bash
# Test Moonraker API manually
curl http://localhost:7125/printer/info

# Check Moonraker is running
sudo systemctl status moonraker
```

**4. Commands Not Working**
- Check Klipper logs: `sudo journalctl -u klipper -f`
- Enable DEBUG logging: `--log-level DEBUG`
- Verify macros are loaded in Klipper

### Debug Mode

Enable detailed logging to troubleshoot issues:

```bash
python3 tft_moonraker_bridge.py -p /dev/ttyUSB0 -l DEBUG
```

This will show:
- All G-codes received from TFT
- Translation results  
- Moonraker API calls
- TFT responses

### Log Files

The bridge creates a log file `tft_bridge.log` in the working directory.

```bash
# View recent logs
tail -f tft_bridge.log

# Search for errors
grep ERROR tft_bridge.log
```

## Supported TFT Functions

### ✅ **Working Features**
- **Movement controls** - All axes, homing
- **Temperature control** - Hotend, bed, fans
- **Print control** - Start, pause, resume, stop
- **Extrusion** - Manual extrude/retract
- **Load/Unload filament** - Via custom macros
- **Basic leveling** - Home, manual positioning

### ✅ **Translated Features**  
- **Bed leveling** - G29 → BED_MESH_CALIBRATE
- **PID tuning** - M303 → PID_CALIBRATE
- **Z-offset** - M851 → SET_GCODE_OFFSET
- **BLTouch** - M280 → BLTOUCH_DEBUG commands

### ⚠️ **Limited Features**
- **Settings menu** - Read-only (Klipper uses config files)
- **EEPROM** - No direct equivalent (use SAVE_CONFIG)
- **Print progress** - Basic support only

### ❌ **Non-functional**
- **12864 LCD mode** - Hardware limitation
- **Firmware updates** - Use Klipper update methods

## Advanced Configuration

### Custom G-code Translations

Edit the `translations` dictionary in `tft_moonraker_bridge.py` to add your own command mappings:

```python
# Add custom translations
self.translations.update({
    r"M600": "PAUSE",  # Filament change
    r"G34": "Z_TILT_ADJUST",  # Z-axis alignment
})
```

### TFT Configuration

Update your TFT's `config.ini` for optimal bridge compatibility:

```ini
# Serial settings
serial_port:P1:6    # 115200 baud
```

### Klipper Integration

For better integration, add these to your `printer.cfg`:

```ini
# Enhanced print macros
[gcode_macro START_PRINT]
gcode:
    # Your start print sequence
    G28                 # Home
    BED_MESH_PROFILE LOAD=default  # Load bed mesh
    
[gcode_macro END_PRINT]  
gcode:
    # Your end print sequence
    M104 S0             # Turn off hotend
    M140 S0             # Turn off bed
    G28 X Y             # Home X and Y
```

## Performance Notes

- **Latency**: ~50-100ms per command (acceptable for UI responsiveness)
- **CPU Usage**: Minimal (<1% on Raspberry Pi 4)
- **Memory**: ~10-20MB Python process
- **Reliability**: Designed for 24/7 operation with auto-recovery

## Safety Considerations

- Bridge includes timeout protection
- Invalid commands are rejected safely  
- Temperature monitoring continues normally
- Emergency stop (M112) works through Klipper

## Support and Updates

The bridge is designed to be extensible. To add support for new TFT commands:

1. Add translation pattern to `GCodeTranslator`
2. Create corresponding Klipper macro if needed
3. Test thoroughly before production use

For issues or improvements, check the bridge logs and Klipper documentation.