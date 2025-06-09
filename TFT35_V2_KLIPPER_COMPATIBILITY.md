# TFT35 V2 Klipper Compatibility Analysis

## Current Status: ⚠️ LIMITED COMPATIBILITY

The BigTreeTech TFT35 V2 has **limited compatibility** with Klipper firmware. While the hardware can communicate with Klipper, many touchscreen features will not work properly due to fundamental differences in communication protocols.

## Compatibility Issues by Command Category

### ✅ COMPATIBLE Commands

These G-codes work reliably with Klipper:

**Basic Movement:**
- `G0/G1` - Move commands ✅
- `G28` - Homing ✅ 
- `G90/G91` - Absolute/relative positioning ✅
- `G92` - Set position ✅

**Temperature Control:**
- `M104/M109` - Hotend temperature ✅
- `M140/M190` - Bed temperature ✅
- `M106/M107` - Fan control ✅

**Basic Print Control:**
- `M24` - Start print ✅
- `M25` - Pause print ✅
- `M114` - Get position ✅

### ⚠️ PARTIALLY COMPATIBLE Commands

These commands exist in Klipper but may behave differently:

**Temperature Reporting:**
- `M105` - Temperature report ⚠️ (Different format)
- `M155` - Auto temperature reporting ⚠️ (May not work as expected)

**Speed/Flow Control:**
- `M220` - Speed factor ⚠️ (Limited support)
- `M221` - Flow factor ⚠️ (Limited support)

**Position Reporting:**
- `M154` - Position auto-report ⚠️ (Not standard in Klipper)

### ❌ INCOMPATIBLE Commands

These TFT35 V2 commands are NOT supported by Klipper:

**Bed Leveling:**
- `M420` - Enable/disable bed leveling ❌
- `M421` - Set mesh value ❌
- `G29` - Auto bed leveling ❌ (Klipper uses different approach)
- `G30` - Single Z-probe ❌
- `G34` - Z-axis auto-alignment ❌

**EEPROM Operations:**
- `M500` - Save settings ❌ (Klipper uses config files)
- `M503` - Report settings ❌

**PID Tuning:**
- `M303` - PID autotune ❌ (Klipper uses different command)

**Firmware Info:**
- `M115` - Firmware info ⚠️ (Different response format)

**BLTouch Commands:**
- `M280` - Servo control ❌ (Klipper uses macros)
- `M401/M402` - Deploy/stow probe ❌
- `M48` - Probe repeatability ❌

**Filament Handling:**
- `M701/M702` - Load/unload filament ❌ (Klipper uses macros)

## Major Functional Limitations

### 1. **Bed Leveling Menu** - ❌ NON-FUNCTIONAL
- Klipper doesn't support standard G29/M420 commands
- Uses `BED_MESH_CALIBRATE` macro instead
- TFT bed leveling interface will not work

### 2. **PID Tuning Menu** - ❌ NON-FUNCTIONAL  
- Klipper uses `PID_CALIBRATE` command, not M303
- TFT PID menu will fail

### 3. **BLTouch Menu** - ❌ NON-FUNCTIONAL
- Klipper doesn't support M280 servo commands
- Uses probe macros like `PROBE_CALIBRATE`

### 4. **Settings/EEPROM Menu** - ❌ NON-FUNCTIONAL
- Klipper uses configuration files, not EEPROM
- M500/M503 commands don't exist

### 5. **Load/Unload Filament** - ❌ NON-FUNCTIONAL
- Requires custom Klipper macros to work

### 6. **Print Progress/Status** - ⚠️ LIMITED
- May not display accurate progress
- Print time estimates may be incorrect

## Workarounds and Solutions

### Option 1: Klipper Macros (Partial Solution)
Create Klipper macros to emulate Marlin commands:

```ini
# In printer.cfg
[gcode_macro M420]
description: Enable/disable bed leveling
gcode:
    {% if params.S|int == 1 %}
        BED_MESH_PROFILE LOAD=default
    {% else %}
        BED_MESH_CLEAR
    {% endif %}

[gcode_macro M701]
description: Load filament
gcode:
    # Your filament load sequence here
    G91
    G1 E50 F300
    G90

[gcode_macro M702] 
description: Unload filament
gcode:
    # Your filament unload sequence here
    G91
    G1 E-50 F300
    G90
```

### Option 2: Use Marlin Mode (12864 Emulation)
- Switch TFT to Marlin mode (12864 LCD emulation)
- Provides basic functionality but loses touchscreen features
- May have display issues

### Option 3: Community Firmware Fork
- Use community-maintained Klipper-compatible TFT firmware
- Search for `neverhags/BIGTREETECH-TouchScreenFirmware-Klipper`
- ⚠️ Not officially supported, use at your own risk

### Option 4: Dedicated Klipper Display
- Consider BTT Pad 7 or similar Klipper-native displays
- Pi-based displays with KlipperScreen
- Better long-term solution

## Recommended Configuration

If you must use TFT35 V2 with Klipper:

1. **Use Basic Functions Only:**
   - Movement controls
   - Temperature settings
   - Basic print start/stop

2. **Avoid These Menus:**
   - Bed leveling
   - PID tuning  
   - BLTouch controls
   - Load/unload filament
   - Settings/EEPROM

3. **Add Klipper Macros:**
   - Implement basic compatibility macros
   - Test thoroughly before relying on them

4. **Consider Alternatives:**
   - Use Klipper web interface for advanced functions
   - Install KlipperScreen on a Pi display
   - Switch to Marlin firmware if TFT functionality is critical

## Bottom Line

While the TFT35 V2 can physically connect to a Klipper system, **most advanced touchscreen features will not work properly**. For full functionality with a touchscreen interface, either:

1. Use Marlin firmware instead of Klipper, OR
2. Use a Klipper-native display solution

The TFT35 V2 was designed for Marlin compatibility and lacks the firmware intelligence to properly interface with Klipper's fundamentally different architecture.