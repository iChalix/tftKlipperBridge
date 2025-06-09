# TFT-Klipper Bridge

This folder contains all the files needed to make your BigTreeTech TFT35 V2 work with Klipper firmware via Moonraker.

## 📁 Folder Contents

### Core Files
- **`tft_moonraker_bridge.py`** - Production-ready bridge script with enhanced security and robustness
- **`tft_moonraker_bridge_original.py`** - Original bridge script (backup/reference only)
- **`klipper_tft_macros.cfg`** - Klipper macros for TFT compatibility (handles existing macros automatically)

### Installation Scripts
- **`install_tft_bridge.sh`** - 🚀 **Interactive installer** with configuration wizard (recommended)
- **`setup_tft_bridge.sh`** - Simple setup script with predefined configuration variables

### Testing Scripts
- **`test_bridge.sh`** - 🧪 **Safe test mode** for testing TFT communication without affecting printer

### Standalone Scripts
- **`run_standalone.sh`** - 🚀 **Zero-setup runner** - auto-detects everything, no installation needed
- **`quick_start.sh`** - ⚡ **One-command download and run** - ultimate convenience

### Version Management
- **`version_check.sh`** - 📋 **Version information** and history management
- **`show_version.py`** - 🏷️ **Dependency-free version display**
- **`VERSION`** - Current version number
- **`CHANGELOG.md`** - Complete version history and changes

### Configuration & Dependencies
- **`tft_bridge_config.template`** - Configuration template with all available options
- **`requirements.txt`** - Python dependencies for easy installation
- **`requirements-dev.txt`** - Additional development dependencies
- **`INSTALL.md`** - Detailed installation instructions

### Documentation
- **`QUICK_START.md`** - 5-minute setup guide
- **`TFT_BRIDGE_SETUP.md`** - Detailed installation and configuration guide
- **`MACRO_COMPATIBILITY.md`** - How the bridge handles existing Klipper macros
- **`TFT35_V2_KLIPPER_COMPATIBILITY.md`** - Complete G-code compatibility analysis
- **`ROBUSTNESS_IMPROVEMENTS.md`** - Analysis of robustness improvements and migration guide

## 🚀 Quick Installation

### Method 1: Interactive Installer (Recommended)
```bash
cd tftKlipperBridge
./install_tft_bridge.sh
```

### Method 2: Simple Setup
```bash
cd tftKlipperBridge
# Edit configuration variables at the top of the script first
./setup_tft_bridge.sh
```

## 🧪 Testing Before Installation

### Safe Test Mode (Recommended)
```bash
cd tftKlipperBridge
./test_bridge.sh                    # Use defaults
./test_bridge.sh /dev/ttyACM0       # Custom serial port
./test_bridge.sh /dev/ttyUSB0 115200 # Custom port and baud rate
```

**Test mode features:**
- ✅ **100% Safe** - No commands sent to printer
- ✅ **Full logging** - See exactly what would be executed
- ✅ **TFT communication** - Test serial connection
- ✅ **Command translation** - Verify G-code mapping
- ✅ **Statistics** - Commands per minute, runtime stats

## 🚀 Zero-Setup Standalone Mode

### Ultimate Convenience - One Command
```bash
# Download and run immediately (no setup required)
curl -sSL https://raw.githubusercontent.com/bigtreetech/BIGTREETECH-TouchScreenFirmware/master/tftKlipperBridge/quick_start.sh | bash
```

### Already Downloaded? Run Standalone
```bash
cd tftKlipperBridge
./run_standalone.sh                    # Interactive setup (recommended)
./run_standalone.sh --test             # Interactive setup, safe test mode
./run_standalone.sh -p /dev/ttyACM0    # Skip setup, use specific port
./run_standalone.sh -y                 # Auto-detect everything, no questions
./run_standalone.sh -b 115200 --verbose # Custom baud + debug
```

**Standalone mode features:**
- ✅ **Zero installation** - no setup scripts needed
- ✅ **Interactive setup** - guides you through serial port selection
- ✅ **Auto-detection** - finds available ports with device info
- ✅ **Permission checking** - validates access and provides fixes
- ✅ **Auto-dependencies** - installs Python packages if missing
- ✅ **Flexible modes** - interactive or fully automatic
- ✅ **Instant start** - from download to running in 30 seconds

## 📋 What You Need

1. **TFT35 V2** connected via USB/serial to your Klipper host
2. **Klipper + Moonraker** running on your 3D printer
3. **Serial port** information (e.g., `/dev/ttyUSB0`)
4. **Baud rate** from your TFT config (usually `250000`)
5. **Python 3.7+** with dependencies installed

### Quick Dependency Install
```bash
# Using requirements.txt (recommended)
pip3 install --user -r requirements.txt

# Or install individually
pip3 install --user pyserial aiohttp websockets requests
```

## ✨ What This Does

The bridge creates a robust, production-ready connection between your TFT touchscreen and Klipper:

- **Intercepts** G-codes from TFT (M104, G28, M701, etc.)
- **Validates and sanitizes** inputs for security
- **Translates** them to Klipper-compatible commands
- **Sends** commands via Moonraker API with retry logic
- **Responds** back to TFT with proper acknowledgments
- **Automatically recovers** from connection failures

## 🎯 Result

After installation, your TFT35 V2 will have:
- ✅ **90%+ functionality restored** with Klipper
- ✅ **Temperature controls** working
- ✅ **Movement and homing** 
- ✅ **Print control** via touchscreen
- ✅ **Bed leveling** (translated to Klipper mesh)
- ✅ **Filament load/unload** (respects your existing macros)

## 🔧 Configuration Variables

Key settings you can customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `TFT_SERIAL_PORT` | `/dev/ttyUSB0` | Serial port for TFT |
| `TFT_BAUD_RATE` | `250000` | Communication speed |
| `MOONRAKER_HOST` | `localhost` | Moonraker IP/hostname |
| `MOONRAKER_PORT` | `7125` | Moonraker port |
| `BRIDGE_LOG_LEVEL` | `INFO` | Debug level |

## 🛠️ Service Management

After installation, control the bridge with:

```bash
# Start/stop/restart
sudo systemctl start tft-bridge
sudo systemctl stop tft-bridge  
sudo systemctl restart tft-bridge

# Check status
sudo systemctl status tft-bridge

# View logs
sudo journalctl -u tft-bridge -f

# Helper scripts (created by installer)
~/bridge_control.sh start|stop|restart
~/bridge_status.sh
~/start_bridge.sh  # Manual testing
```

## 🔍 Troubleshooting

### TFT Shows "No Printer Attached"
```bash
# Check bridge service
sudo systemctl status tft-bridge

# Check serial connection
ls -la /dev/ttyUSB*

# View debug logs
sudo journalctl -u tft-bridge -f
```

### Permission Issues
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in, then restart bridge
```

## 📚 Documentation

- **New to this?** Start with `QUICK_START.md`
- **Need details?** See `TFT_BRIDGE_SETUP.md`
- **Have existing macros?** Check `MACRO_COMPATIBILITY.md`
- **Want compatibility info?** Read `TFT35_V2_KLIPPER_COMPATIBILITY.md`

## 🤝 Macro Compatibility

The bridge automatically detects and respects your existing Klipper macros:

- ✅ **Existing `LOAD_FILAMENT`/`UNLOAD_FILAMENT` macros** → Uses your macros
- ✅ **No existing macros** → Provides simple fallback macros
- ✅ **No conflicts** → Your custom logic is preserved

## 🔄 Updates

To update the bridge:
1. Download new `tft_moonraker_bridge.py`
2. Replace the file in your installation directory
3. Restart the service: `sudo systemctl restart tft-bridge`

## 📋 Version Management

### Check Version Information
```bash
# Quick version check
./version_check.sh info

# Show all version info
./version_check.sh all

# Compare script vs file versions
./version_check.sh compare

# Show version history
./version_check.sh history
```

### Version Commands (Built-in)
```bash
# Show current version
python3 tft_moonraker_bridge.py --version

# Show version history
python3 tft_moonraker_bridge.py --version-history

# Show specific version details
python3 tft_moonraker_bridge.py --version-info 2.0.0

# Dependency-free version check
python3 show_version.py
```

### Current Version Features
- **v2.2.0** - Latest with interactive setup, dependency management, and professional documentation
- **Compatibility** - Requires Python 3.7+ (automatic checking)
- **Dependencies** - Auto-installs via requirements.txt in standalone mode
- **Upgrade Path** - Fully backwards compatible from v2.0+

## ⚠️ Important Notes

- **Backup your configs** before installation
- **Test manually first** using the start script
- **Monitor logs initially** to catch issues early
- **Restart Klipper** after adding macros

## 🆘 Support

If you encounter issues:
1. Check the logs: `sudo journalctl -u tft-bridge -f`
2. Enable debug mode: Set `BRIDGE_LOG_LEVEL="DEBUG"`
3. Verify serial connection and permissions
4. Ensure Moonraker is accessible

---

**Ready to get started?** Run `./install_tft_bridge.sh` and follow the prompts! 🎉