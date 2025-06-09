# TFT-Moonraker Bridge Quick Start Guide

Get your TFT35 V2 working with Klipper in 5 minutes!

## 🚀 Super Quick Installation

### 1. Download Repository
Clone or download the BIGTREETECH-TouchScreenFirmware repository to your Klipper host (Raspberry Pi, etc.)

### 2. Navigate to Bridge Folder
```bash
cd BIGTREETECH-TouchScreenFirmware/tftKlipperBridge
```

### 3. Run Installation Script
```bash
# Run the enhanced installer (recommended)
./install_tft_bridge.sh

# OR run the basic setup script (edit variables first)
./setup_tft_bridge.sh
```

### 4. Follow the Prompts
The installer will ask for:
- **Serial port** (e.g., `/dev/ttyUSB0`)
- **Baud rate** (usually `250000`)
- **Moonraker host** (usually `localhost`)

### 5. Start the Service
```bash
# Restart Klipper first
sudo systemctl restart klipper

# Start the bridge
sudo systemctl start tft-bridge

# Check it's working
sudo systemctl status tft-bridge
```

**That's it!** Your TFT should now work with Klipper! 🎉

---

## 📋 What You Need

### Hardware
- TFT35 V2 touchscreen
- USB-to-serial cable or direct USB connection
- Klipper-based 3D printer

### Software Requirements
- Klipper firmware on your printer
- Moonraker installed and running
- Python 3.7+ (usually pre-installed)

### Connection Setup
1. **Connect TFT to your Klipper host** via USB or serial
2. **Note the serial port** (usually `/dev/ttyUSB0` or `/dev/ttyACM0`)
3. **Check TFT baud rate** in your TFT's `config.ini`

---

## 🔧 Configuration Options

### Easy Configuration (Recommended)
The installer creates a config file you can edit:
```bash
nano ~/tft_bridge_config.sh
```

### Manual Configuration Variables
Edit these in the setup script or config file:

| Variable | Default | Description |
|----------|---------|-------------|
| `TFT_SERIAL_PORT` | `/dev/ttyUSB0` | Serial port for TFT |
| `TFT_BAUD_RATE` | `250000` | Communication speed |
| `MOONRAKER_HOST` | `localhost` | Moonraker IP/hostname |
| `MOONRAKER_PORT` | `7125` | Moonraker port |
| `BRIDGE_LOG_LEVEL` | `INFO` | Logging detail level |
| `AUTO_START` | `yes` | Start on boot |

---

## 🎛️ Service Control

### Basic Commands
```bash
# Start/stop/restart
sudo systemctl start tft-bridge
sudo systemctl stop tft-bridge  
sudo systemctl restart tft-bridge

# Check status
sudo systemctl status tft-bridge

# View logs
sudo journalctl -u tft-bridge -f
```

### Helper Scripts (created by installer)
```bash
# Quick control
~/bridge_control.sh start|stop|restart|status|logs

# Check status
~/bridge_status.sh

# Manual start (for testing)
~/start_bridge.sh
```

---

## 🔍 Troubleshooting

### TFT Shows "No Printer Attached"
```bash
# Check service is running
sudo systemctl status tft-bridge

# Check serial connection
ls -la /dev/ttyUSB*

# View logs for errors
sudo journalctl -u tft-bridge -f
```

### "Permission Denied" on Serial Port
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in, then restart service
sudo systemctl restart tft-bridge
```

### Commands Not Working
```bash
# Check Klipper macros are loaded
# Look for "TFT Bridge Macros" in web interface

# Restart Klipper to reload macros
sudo systemctl restart klipper

# Enable debug logging
# Edit ~/tft_bridge_config.sh, set BRIDGE_LOG_LEVEL="DEBUG"
sudo systemctl restart tft-bridge
```

### Moonraker Connection Failed
```bash
# Test Moonraker API
curl http://localhost:7125/printer/info

# Check Moonraker is running
sudo systemctl status moonraker
```

---

## ✅ What Works After Installation

### Fully Working ✅
- **Movement controls** - X/Y/Z axes, homing
- **Temperature control** - Hotend, bed, fans  
- **Print control** - Start, pause, resume, stop
- **Extrusion** - Manual extrude/retract
- **File browsing** - SD card and USB files

### Translated Features ✅
- **Bed leveling** - Uses Klipper mesh bed leveling
- **Filament load/unload** - Via custom macros
- **PID tuning** - Translated to Klipper commands
- **Z-offset adjustment** - Uses Klipper offset system
- **BLTouch controls** - Via Klipper probe commands

### Limited Features ⚠️
- **Settings menu** - Read-only (Klipper uses config files)
- **Print progress** - Basic support only

---

## 📈 Performance

- **Response time**: ~50-100ms per command
- **CPU usage**: <1% on Raspberry Pi 4
- **Memory usage**: ~10-20MB
- **Reliability**: Designed for 24/7 operation

---

## 🆘 Getting Help

### Log Files
- Bridge logs: `sudo journalctl -u tft-bridge -f`
- Klipper logs: `sudo journalctl -u klipper -f` 
- File logs: `~/tft_bridge.log`

### Debug Mode
Enable detailed logging:
```bash
# Edit config file
nano ~/tft_bridge_config.sh
# Change: BRIDGE_LOG_LEVEL="DEBUG"

# Restart service
sudo systemctl restart tft-bridge

# Watch detailed logs
sudo journalctl -u tft-bridge -f
```

### Common Issues
1. **Serial port permissions** → Add user to dialout group
2. **Wrong baud rate** → Check TFT config.ini file
3. **Moonraker not accessible** → Check IP/port settings
4. **Macros not working** → Restart Klipper after installation

---

## 🔄 Updates and Maintenance

### Updating the Bridge
```bash
# Download new version
# Replace tft_moonraker_bridge.py

# Restart service
sudo systemctl restart tft-bridge
```

### Backup Configuration
```bash
# Backup your settings
cp ~/tft_bridge_config.sh ~/tft_bridge_config.sh.backup
```

---

## 💡 Pro Tips

1. **Test manually first**: Use `~/start_bridge.sh` to test before enabling service
2. **Monitor logs initially**: Watch logs during first use to catch issues
3. **Keep TFT firmware updated**: Use latest TFT firmware for best compatibility
4. **Customize macros**: Edit Klipper macros to match your printer setup
5. **Use debug mode**: Enable when troubleshooting issues

**Enjoy your Klipper-compatible TFT35 V2!** 🎯