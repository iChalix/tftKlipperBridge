# G-codes and M-codes used by TFT35 V2

This document provides a comprehensive list of G-codes and M-codes that are sent by the TFT35 V2 touchscreen when using various menu functions.

## Movement Commands

### G-codes
- **G0**: Rapid positioning move
  - Used in Move menu: `G0 X%.2f F%d` (X axis movement)
  - Used in Move menu: `G0 Y%.2f F%d` (Y axis movement)
  - Used in Move menu: `G0 Z%.2f F%d` (Z axis movement)

- **G1**: Linear move with specified feedrate
  - Used in Extrude menu: `G1 E%.5f F%d` (Extrusion/retraction)

- **G28**: Home axes
  - Home menu: `G28` (Home all axes)
  - Home menu: `G28 X` (Home X axis)
  - Home menu: `G28 Y` (Home Y axis)
  - Home menu: `G28 Z` (Home Z axis)
  - BLTouch menu: Used before M48 repeatability test

- **G90**: Set to absolute positioning mode
  - Used after exiting Move menu

- **G91**: Set to relative positioning mode
  - Used when entering Move menu

- **G92**: Set position
  - Used in Extrude menu: `G92 E%.5f` (Set E axis position)

## Bed Leveling Commands

### G-codes
- **G26**: Mesh validation pattern
- **G29**: Auto bed leveling
  - BBL (Bilinear): `G29`
  - UBL (Unified): `G29 P1` (Phase 1 - Deploy probe and measure)
  - UBL: `G29 P3` (Phase 3 - Smart fill missing points)
  - UBL: `G29 P5 C` (Phase 5 - Find mean mesh height)
  - UBL: `G29 L[slot]` (Load mesh from slot)
  - UBL: `G29 S[slot]` (Save mesh to slot)
- **G30**: Single Z-probe
- **G33**: Delta calibration
- **G34**: Z-axis auto-alignment
- **G42**: Move to mesh coordinate

### M-codes
- **M420**: Enable/disable bed leveling
- **M421**: Set mesh value

## Temperature Commands

### M-codes
- **M104**: Set hotend temperature
- **M105**: Report temperatures
- **M106**: Set fan speed
- **M107**: Turn fan off
- **M109**: Wait for hotend temperature
- **M140**: Set bed temperature
- **M190**: Wait for bed temperature
- **M154**: Set position auto-report interval
- **M155**: Set temperature auto-report interval
- **M303**: PID autotune
  - For Marlin: `M303 E0 C8 U1` (Hotend 0)
  - For Marlin: `M303 E1 C8 U1` (Hotend 1) 
  - For Marlin: `M303 E-1 C8 U1` (Bed)
  - For RepRapFirmware: `M303 T0` (Tool 0)
  - For RepRapFirmware: `M303 H0` (Bed heater)
- **M306**: MPC (Model Predictive Control) tuning

## Movement Control

### M-codes
- **M18**: Disable steppers (same as M84)
- **M84**: Disable steppers
  - Manual Leveling: `M84 X Y E` (Unlock XY and E axes)

- **M82**: Set extruder to absolute mode
- **M83**: Set extruder to relative mode

- **M92**: Set axis steps per unit

- **M114**: Get current position
  - Used in Move menu to query position

## Speed and Flow Control

### M-codes
- **M220**: Set feedrate percentage
- **M221**: Set flow percentage

## BLTouch/Servo Commands

### M-codes
- **M280**: Servo position
  - BLTouch menu: `M280 P0 S160` (Reset)
  - BLTouch menu: `M280 P0 S120` (Test/Self-test)
  - BLTouch menu: `M280 P0 S10` (Deploy)
  - BLTouch menu: `M280 P0 S90` (Stow)

- **M401**: Deploy probe
  - With `H` parameter to get High Speed mode status
  - With `S` parameter to set High Speed mode

- **M48**: Probe repeatability test

## Probe Offset

### M-codes
- **M851**: Set/report Z probe offset

## File Operations

### M-codes
- **M20**: List SD card files
- **M21**: Initialize SD card
- **M23**: Select file
- **M24**: Start/resume print
- **M25**: Pause print
- **M27**: Report print progress
- **M33**: Get file info
- **M36**: Get file info (alternative)
- **M125**: Park head (pause print)

## Load/Unload Filament

### M-codes
- **M701**: Load filament
- **M702**: Unload filament

## Configuration and EEPROM

### M-codes
- **M500**: Save settings to EEPROM
- **M503**: Report settings
  - Settings menu: `M503 S0` (Report settings without saving)

- **M115**: Get firmware info

## Endstop and Motion

### M-codes
- **M206**: Set home offset
- **M211**: Software endstops
- **M569**: Set motor direction

## Communication

### M-codes
- **M117**: Display message on LCD
- **M118**: Serial print

## Other Commands

### M-codes
- **M0**: Unconditional stop
- **M81**: Power off
- **M150**: Set RGB LED color
  - For Marlin: `M150 R[red] U[green] B[blue] W[white] P[brightness] I[index]`
  - For RepRapFirmware: `M150 X2 R[red] U[green] B[blue] P[brightness]`
- **M290**: Babystepping
- **M355**: Case light control
- **M376**: Fade height
- **M710**: Controller fan settings

## RepRapFirmware Specific

### M-codes
- **M408**: Report JSON status
- **M409**: Query object model
- **M552**: Network interface control

## Usage Context

The TFT35 V2 sends these commands in response to user interactions:

1. **Navigation**: Home menu, Move menu
2. **Temperature Control**: Heat menu, printing screen
3. **Extrusion**: Extrude menu, Load/Unload menu
4. **Leveling**: Manual Leveling, ABL, BLTouch menus
5. **Printing**: Print control, pause/resume, stop
6. **Configuration**: Settings menus

## Additional Features

### Custom G-codes
The TFT35 V2 supports custom G-codes that can be configured through the config.ini file on the SD card. This allows users to add their own frequently used commands to the interface.

### Terminal Mode
The TFT35 V2 includes a terminal mode that allows direct sending of any G-code or M-code command to the printer, useful for:
- Testing new commands
- Debugging printer behavior
- Sending commands not available in the standard menus

### Marlin Mode
The TFT35 V2 can switch between Touch Mode and Marlin Mode (emulating a standard 12864 LCD), where it acts as a traditional display and the printer's mainboard handles all the menu logic.

## Important Notes

1. **Firmware Compatibility**: The actual availability of these commands depends on the firmware running on your 3D printer's mainboard (Marlin, RepRapFirmware, etc.).

2. **Command Parameters**: Many commands accept additional parameters not shown in every example. Refer to your firmware's documentation for complete parameter lists.

3. **Safety**: Always ensure your printer is properly configured before using commands that involve movement or heating.

4. **Auto-reporting**: The TFT uses M154 and M155 for automatic position and temperature reporting to reduce the need for constant polling.