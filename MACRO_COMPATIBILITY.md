# Macro Compatibility Guide

## Handling Existing LOAD_FILAMENT and UNLOAD_FILAMENT Macros

The TFT bridge is designed to work seamlessly with your existing Klipper macros. Here's how it handles conflicts:

## 🔄 **How It Works**

### 1. **Smart Detection**
The bridge automatically detects if you already have `LOAD_FILAMENT` and `UNLOAD_FILAMENT` macros in your Klipper configuration.

### 2. **Existing Macros Priority**
- ✅ **If you have existing macros**: Your macros will be used
- ✅ **If no existing macros**: Fallback macros will be provided
- ✅ **No conflicts**: Your existing macros remain untouched

### 3. **Runtime Detection**
The bridge checks your Klipper configuration at startup and adapts automatically:

```python
# Bridge logic
if "LOAD_FILAMENT" in available_macros:
    # Use your existing macro
    return "LOAD_FILAMENT"
else:
    # Use fallback macro
    return "TFT_LOAD_FILAMENT"
```

## 📋 **What Gets Installed**

### M701/M702 Translation Macros
These handle the TFT's M701 and M702 commands:

```ini
[gcode_macro M701]
description: Load filament (uses existing macro if available)
gcode:
    {% if printer['gcode_macro LOAD_FILAMENT'] is defined %}
        LOAD_FILAMENT {rawparams}  # Uses YOUR macro
    {% else %}
        TFT_LOAD_FILAMENT {rawparams}  # Uses fallback
    {% endif %}

[gcode_macro M702]  
description: Unload filament (uses existing macro if available)
gcode:
    {% if printer['gcode_macro UNLOAD_FILAMENT'] is defined %}
        UNLOAD_FILAMENT {rawparams}  # Uses YOUR macro
    {% else %}
        TFT_UNLOAD_FILAMENT {rawparams}  # Uses fallback
    {% endif %}
```

### Fallback Macros (Only Used If Needed)
```ini
[gcode_macro TFT_LOAD_FILAMENT]
description: TFT fallback load filament macro
# Simple load logic - only used if you don't have LOAD_FILAMENT

[gcode_macro TFT_UNLOAD_FILAMENT]  
description: TFT fallback unload filament macro
# Simple unload logic - only used if you don't have UNLOAD_FILAMENT
```

## ✅ **Benefits of This Approach**

1. **No Conflicts**: Your existing macros are never overwritten
2. **Automatic Detection**: Works without manual configuration
3. **Fallback Safety**: Provides basic functionality if no macros exist
4. **Parameter Passing**: Your macro parameters are preserved
5. **Custom Logic**: Your complex filament handling logic remains intact

## 🔧 **Configuration Examples**

### Scenario 1: You Have Existing Macros
Your printer.cfg:
```ini
[gcode_macro LOAD_FILAMENT]
gcode:
    # Your custom filament loading logic
    HEAT_EXTRUDER
    PRESENT_FILAMENT
    LOAD_TO_EXTRUDER
    # etc.

[gcode_macro UNLOAD_FILAMENT]
gcode:
    # Your custom filament unloading logic
    HEAT_EXTRUDER
    RETRACT_FILAMENT
    PARK_FILAMENT
    # etc.
```

**Result**: 
- TFT M701/M702 commands will call YOUR macros
- Your custom heating, parking, and safety logic is preserved
- Bridge logs: "Using existing LOAD_FILAMENT macro"

### Scenario 2: No Existing Macros
Your printer.cfg:
```ini
# No LOAD_FILAMENT or UNLOAD_FILAMENT macros defined
```

**Result**: 
- TFT M701/M702 commands will use the simple fallback macros
- Basic extrude/retract functionality provided
- Bridge logs: "No LOAD_FILAMENT macro found, using fallback"

## 🎯 **Best Practices**

### If You Have Complex Filament Macros
```ini
# Your existing macro (example)
[gcode_macro LOAD_FILAMENT]
gcode:
    {% set TEMP = params.TEMP|default(200)|float %}
    {% set DISTANCE = params.DISTANCE|default(50)|float %}
    
    M109 S{TEMP}           # Heat and wait
    G91                    # Relative mode
    G1 E{DISTANCE} F300    # Load filament
    G90                    # Absolute mode
    M400                   # Wait for moves
    BEEP_SOUND             # Audio feedback
```

**The bridge will use this macro**, preserving all your custom logic!

### If You Want to Customize Fallback Behavior
Edit the `TFT_LOAD_FILAMENT` and `TFT_UNLOAD_FILAMENT` macros in `klipper_tft_macros.cfg`:

```ini
[gcode_macro TFT_LOAD_FILAMENT]
description: TFT fallback load filament macro
gcode:
    # Customize this for your printer if you don't have LOAD_FILAMENT
    {% set speed = params.SPEED|default(300)|int %}
    {% set load_distance = params.LENGTH|default(50)|int %}
    
    # Add your custom logic here
    M109 S200              # Heat extruder first
    G91                    # Relative positioning
    G92 E0                 # Reset extruder
    G1 E{load_distance} F{speed * 60}  # Load filament
    G90                    # Back to absolute
    RESPOND MSG="Filament loaded"
```

## 🔍 **Troubleshooting**

### Check What Macros Are Detected
Enable debug logging to see what macros the bridge finds:

```bash
# Edit config
nano ~/tft_bridge_config.sh
# Set: BRIDGE_LOG_LEVEL="DEBUG"

# Restart bridge
sudo systemctl restart tft-bridge

# View logs
sudo journalctl -u tft-bridge -f
```

Look for logs like:
```
Found 15 available macros
Available macros: ['LOAD_FILAMENT', 'UNLOAD_FILAMENT', 'START_PRINT', ...]
Using existing LOAD_FILAMENT macro
```

### Force Using Your Macros
If detection fails, you can force the bridge to use your macros by editing the bridge script's translation dictionary:

```python
# In tft_moonraker_bridge.py, around line 146
"M701": "LOAD_FILAMENT",      # Force use your macro
"M702": "UNLOAD_FILAMENT",    # Force use your macro
```

### Manual Override
You can also create override macros that call your existing ones:

```ini
[gcode_macro M701]
gcode:
    MY_CUSTOM_LOAD_MACRO {rawparams}

[gcode_macro M702]  
gcode:
    MY_CUSTOM_UNLOAD_MACRO {rawparams}
```

## 📚 **Summary**

The TFT bridge system is designed to:
- ✅ **Respect your existing macros**
- ✅ **Provide fallbacks when needed**
- ✅ **Detect conflicts automatically**
- ✅ **Preserve your custom logic**
- ✅ **Work out of the box**

You don't need to modify or remove your existing `LOAD_FILAMENT` and `UNLOAD_FILAMENT` macros. The bridge will detect and use them automatically! 🎉