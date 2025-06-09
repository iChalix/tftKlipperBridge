# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a TFT-Klipper Bridge system that acts as a translator between BigTreeTech TFT35 V2 touchscreens and Klipper 3D printer firmware via Moonraker. The bridge intercepts G-codes from the TFT, validates and translates them to Klipper-compatible commands, and forwards them through the Moonraker API.

## Core Architecture

The system consists of several key components:

- **TFTMoonrakerBridge**: Main orchestrator class that coordinates all components
- **TFTSerial**: Handles serial communication with the TFT touchscreen
- **MoonrakerClient**: Manages HTTP/WebSocket communication with Moonraker API
- **GCodeTranslator**: Translates TFT G-codes to Klipper macros/commands
- **ConnectionManager**: Handles connection pooling and automatic reconnection
- **SecurityValidator**: Validates and sanitizes all inputs for security

The bridge operates asynchronously using asyncio and includes comprehensive error handling, rate limiting, and automatic recovery mechanisms.

## Common Development Commands

### Running the Bridge
```bash
# Production mode
python3 tft_moonraker_bridge.py --serial-port /dev/ttyUSB0 --baud-rate 250000

# Test mode (safe, no commands executed)
python3 tft_moonraker_bridge.py --serial-port /dev/ttyUSB0 --test-mode

# Standalone mode (auto-setup)
./run_standalone.sh

# Test via wrapper script
./test_bridge.sh /dev/ttyUSB0 250000
```

### Installation and Setup
```bash
# Interactive installer (recommended)
./install_tft_bridge.sh

# Quick setup
./setup_tft_bridge.sh

# Uninstall (complete removal)
./uninstall_tft_bridge.sh

# Check dependencies
python3 check_dependencies.py

# Install Python dependencies
pip3 install --user -r requirements.txt
```

### Development Dependencies
```bash
# Install development tools
pip3 install --user -r requirements-dev.txt

# Code formatting and linting
black tft_moonraker_bridge.py
flake8 tft_moonraker_bridge.py
mypy tft_moonraker_bridge.py

# Testing
pytest tests/ --cov=tft_moonraker_bridge
```

### Service Management
```bash
# Control systemd service (if installed)
sudo systemctl start tft-bridge
sudo systemctl stop tft-bridge
sudo systemctl status tft-bridge
sudo journalctl -u tft-bridge -f

# Helper scripts (created by installer)
~/bridge_control.sh start|stop|restart
~/bridge_status.sh
```

### Version and Debugging
```bash
# Version information
python3 tft_moonraker_bridge.py --version
python3 tft_moonraker_bridge.py --version-history

# List detected Klipper macros
python3 tft_moonraker_bridge.py --list-macros

# Version checking utilities
./version_check.sh info
python3 show_version.py
```

## Key Configuration

The bridge uses a dataclass-based configuration system (`BridgeConfig`) with validation. Key parameters:

- `serial_port`: TFT serial device (e.g., /dev/ttyUSB0)
- `baud_rate`: Communication speed (typically 250000)
- `moonraker_host/port`: Moonraker API location (localhost:7125)
- `test_mode`: Safe mode that logs but doesn't execute commands
- `standalone_mode`: Auto-detection and minimal setup mode

## Security Considerations

The bridge includes multiple security layers:
- Input sanitization for all G-codes and filenames
- Path traversal protection for file operations
- Rate limiting to prevent API flooding
- Command length validation
- Automatic connection management with retry limits

## Testing Approach

The project uses a multi-layered testing strategy:
- **Test mode**: Safe simulation without affecting the printer
- **Integration testing**: Uses actual TFT hardware in safe mode
- **Unit testing**: Component-level tests (pytest framework)
- **Manual testing**: Scripts for real-world validation

When adding new features:
1. Implement with test mode support first
2. Add unit tests for new components
3. Test with actual hardware in test mode
4. Validate with real printer operations

## Macro System

The bridge intelligently handles Klipper macros:
- Detects existing user macros and uses them preferentially
- Provides fallback macros for missing functionality
- Never overwrites existing macro definitions
- Supports dynamic macro detection during runtime

## Error Handling Philosophy

The bridge follows a "never crash" philosophy:
- All network operations include retry logic with exponential backoff
- Serial communication errors trigger automatic reconnection
- Missing dependencies are detected and reported clearly
- The bridge continues running even if individual components fail

## File Structure Notes

- `tft_moonraker_bridge.py`: Main production script
- `tft_moonraker_bridge_original.py`: Original reference implementation
- `klipper_tft_macros.cfg`: Fallback macros for Klipper integration
- Installation scripts (`install_*`, `setup_*`, `run_standalone.sh`)
- Documentation files for various aspects of the system
- Version management utilities and templates