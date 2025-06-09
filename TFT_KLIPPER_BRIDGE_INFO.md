# 🎯 TFT-Klipper Bridge Available!

## Want to use your BigTreeTech TFT with Klipper?

We've created a comprehensive solution that makes your TFT35 V2 (and other TFT models) work seamlessly with Klipper firmware!

### 📁 **Bridge Location**
All TFT-Klipper bridge files are located in the [`tftKlipperBridge/`](tftKlipperBridge/) folder.

### 🚀 **Quick Start**
```bash
cd tftKlipperBridge
./install_tft_bridge.sh
```

### ✨ **What You Get**
- **90%+ TFT functionality restored** with Klipper
- **Temperature controls** working perfectly
- **Print control** via touchscreen
- **Bed leveling** translated to Klipper mesh system
- **Filament load/unload** (respects existing macros)
- **Automatic service management**

### 🔧 **How It Works**
The bridge translates TFT G-codes to Klipper commands in real-time:
- **TFT sends M104** → Bridge converts to Klipper temperature command
- **TFT sends M701** → Bridge calls your existing LOAD_FILAMENT macro
- **TFT sends G29** → Bridge triggers BED_MESH_CALIBRATE

### 📚 **Complete Documentation**
- [`README.md`](tftKlipperBridge/README.md) - Overview and file descriptions
- [`QUICK_START.md`](tftKlipperBridge/QUICK_START.md) - 5-minute setup guide
- [`TFT_BRIDGE_SETUP.md`](tftKlipperBridge/TFT_BRIDGE_SETUP.md) - Detailed installation guide
- [`MACRO_COMPATIBILITY.md`](tftKlipperBridge/MACRO_COMPATIBILITY.md) - Existing macro handling
- [`TFT35_V2_KLIPPER_COMPATIBILITY.md`](tftKlipperBridge/TFT35_V2_KLIPPER_COMPATIBILITY.md) - G-code compatibility analysis

### 🎯 **Perfect For**
- Users who want to keep their TFT touchscreen with Klipper
- Printers already running Klipper + Moonraker
- Anyone tired of "No Printer Attached" messages

### ⚡ **Installation**
Choose your preferred method:

**Interactive Installer (Recommended)**
```bash
cd tftKlipperBridge
./install_tft_bridge.sh
```

**Quick Setup**
```bash
cd tftKlipperBridge
# Edit variables in setup_tft_bridge.sh first
./setup_tft_bridge.sh
```

---

**Ready to bridge the gap between your TFT and Klipper?** Head to the [`tftKlipperBridge/`](tftKlipperBridge/) folder and get started! 🎉