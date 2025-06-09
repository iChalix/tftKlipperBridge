# TFT-Moonraker Bridge v2.2.0 Release Notes

**Release Date:** June 9, 2024  
**Version:** 2.2.0  
**Compatibility:** Fully backwards compatible with v2.0+  

## 🎯 **What's New in v2.2.0**

### 🚀 **Enhanced Standalone Experience**
- **Interactive Serial Port Setup** - Guides users through port selection with device information
- **Smart Auto-Detection** - Automatically finds and validates TFT devices
- **Permission Validation** - Checks access and provides exact fix commands
- **Guided Configuration** - Step-by-step setup for baud rates and options

### 📦 **Professional Dependency Management**
- **requirements.txt** - Standard Python dependency specification
- **requirements-dev.txt** - Development and testing tools
- **Auto-Installation** - Standalone mode automatically installs missing packages
- **Better Error Handling** - Clear guidance when dependencies fail

### 📚 **Comprehensive Documentation**
- **INSTALL.md** - Complete installation guide with troubleshooting
- **Enhanced README** - Improved examples and usage scenarios
- **Version Management** - Professional changelog and version tracking

### 🔧 **Improved Automation**
- **Non-Interactive Mode** (`-y` flag) - Perfect for scripts and automation
- **Better CLI Arguments** - More flexible command-line interface
- **Enhanced Error Recovery** - Graceful handling of setup failures

## 🆕 **New Features**

### Interactive Port Selection
```bash
./run_standalone.sh

Detecting serial ports...
Found 2 serial port(s):

[1] /dev/ttyUSB0
Port: /dev/ttyUSB0
  ID_VENDOR: BigTreeTech
  ID_MODEL: TFT35_V2
  ✓ Accessible

[2] /dev/ttyACM0
Port: /dev/ttyACM0
  ✗ Permission denied
    Run: sudo usermod -a -G dialout pi

Select serial port:
  1) /dev/ttyUSB0
  2) /dev/ttyACM0
  m) Enter manually

Choice [1]: █
```

### Professional Dependency Management
```bash
# New standard way
pip3 install --user -r requirements.txt

# Automatic in standalone mode
./run_standalone.sh  # Auto-installs if needed
```

### Enhanced Installation Options
```bash
# Interactive setup (new default)
./run_standalone.sh

# Automation-friendly
./run_standalone.sh -y

# Specific configuration
./run_standalone.sh -p /dev/ttyACM0 -b 115200

# Safe testing
./run_standalone.sh --test
```

## 🔄 **Migration Guide**

### From v2.1.x → v2.2.x
**Status: ✅ Drop-in replacement - no changes needed**

- All existing installations continue to work
- New features are optional and don't affect existing setups
- Enhanced standalone script provides better user experience
- Consider using `requirements.txt` for future dependency management

### Recommended Actions
1. **Update the bridge script**: Replace `tft_moonraker_bridge.py`
2. **Update standalone script**: Replace `run_standalone.sh` (optional, for better UX)
3. **Add requirements.txt**: Download for easier dependency management
4. **Test the update**: Use `--test-mode` to verify functionality

## 📊 **Technical Improvements**

### Code Quality
- Enhanced error handling in standalone script
- Better argument processing and validation
- Improved user feedback and guidance
- More robust dependency detection

### User Experience
- Interactive setup reduces configuration errors
- Clear device information helps identify correct ports
- Permission issues are detected and solutions provided
- Non-interactive mode supports automation needs

### Documentation
- Professional installation guide with troubleshooting
- Complete dependency specification
- Version tracking and changelog maintenance
- Clear upgrade paths and compatibility information

## 🛡️ **Backwards Compatibility**

✅ **Fully Compatible** with:
- All v2.1.x installations
- All v2.0.x installations  
- Existing configuration files
- Current systemd services
- All command-line interfaces

❌ **Not Compatible** with:
- v1.x installations (use v2.0.0 migration guide)

## 📦 **Distribution**

**Download:** `tftKlipperBridge.tar.gz` (51KB)  
**Files:** 25 total files  
**Requirements:** Python 3.7+  

### Quick Installation
```bash
# Download and extract
tar -xzf tftKlipperBridge.tar.gz
cd tftKlipperBridge

# Interactive setup
./run_standalone.sh

# Or full installation
./install_tft_bridge.sh
```

## 🎉 **Summary**

Version 2.2.0 transforms the TFT-Moonraker Bridge from a technical tool into a **user-friendly, professional solution**:

- **Beginners** get guided interactive setup
- **Experts** get automation-friendly options  
- **Developers** get proper dependency management
- **Everyone** gets better documentation and error handling

This release maintains **100% backwards compatibility** while significantly improving the user experience for new installations and setup scenarios.

---

**Ready to upgrade?** Download v2.2.0 and enjoy the enhanced installation experience! 🚀