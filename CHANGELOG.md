# TFT-Moonraker Bridge Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2024-06-09

### Added
- **Enhanced standalone script with interactive setup**
  - Interactive serial port detection and selection
  - Device information display (vendor, model, serial)
  - Permission validation with helpful error messages
  - Smart auto-selection for single port scenarios
  - Guided baud rate selection with common presets
- **Professional dependency management**
  - `requirements.txt` for production dependencies
  - `requirements-dev.txt` for development tools
  - Automatic dependency installation in standalone mode
  - Updated installation scripts to use requirements files
- **Comprehensive installation documentation**
  - `INSTALL.md` with detailed setup instructions
  - Multiple installation method documentation
  - Python version compatibility matrix
  - Troubleshooting guides for common issues
- **Improved automation support**
  - Non-interactive mode (`-y` flag) for automation
  - Better argument handling in standalone script
  - Enhanced error handling and recovery

### Changed
- **Standalone script user experience**
  - Default mode is now interactive (guides users through setup)
  - Better help text and usage examples
  - Improved configuration display
- **Installation scripts**
  - Now prefer `requirements.txt` over individual package installation
  - Enhanced error handling for dependency installation
  - Better fallback mechanisms

### Fixed
- Improved serial port detection across different Linux distributions
- Better handling of permission issues with actionable solutions
- Enhanced command-line argument processing in standalone mode

## [2.1.0] - 2024-06-09

### Added
- **Comprehensive version handling system**
  - Version information embedded in code
  - Command line version flags (`--version`, `--version-history`)
  - Version included in M115 firmware response
  - Python compatibility checking
- **Standalone mode for zero-setup operation**
  - Auto-detection of serial ports
  - Automatic dependency installation
  - Runs without configuration files
  - Perfect for testing and quick deployment
- **Enhanced connection resilience**
  - Bridge never stops on connection failures
  - Continuous monitoring and reconnection
  - Graceful handling of Moonraker/TFT disconnections
- **Test mode for safe operation**
  - Commands logged but not executed
  - Safe for testing TFT communication
  - Performance statistics tracking
- **Improved error handling and recovery**
  - Better error context and logging
  - Fallback responses when systems unavailable
  - Always responds to TFT to prevent timeouts

### Changed
- Bridge startup now displays version and build information
- M115 responses now include bridge version
- Improved configuration validation (permissive in standalone mode)
- Enhanced documentation with usage examples

### Fixed
- Connection failures no longer cause bridge to exit
- Better handling of missing dependencies in standalone mode
- Improved serial port validation

## [2.0.0] - 2024-06-08

### Added
- **Complete robustness overhaul**
  - Security validation and input sanitization
  - Protection against path traversal and command injection
  - Input validation for all parameters
- **Async HTTP with connection pooling**
  - Replaced synchronous requests with aiohttp
  - Connection pooling for better performance
  - Proper async/await throughout codebase
- **Rate limiting and resource management**
  - Configurable rate limits for API calls
  - Comprehensive connection cleanup
  - Memory leak prevention
- **Enhanced error handling**
  - Retry logic with exponential backoff
  - Specific exception handling
  - Better error context and recovery

### Changed
- **Breaking**: Replaced `requests` library with `aiohttp`
- **Breaking**: Modified configuration validation requirements
- Improved logging with rotation support
- Better signal handling for graceful shutdown

### Security
- Added input sanitization to prevent injection attacks
- Filename validation to prevent path traversal
- Limited input lengths to prevent buffer overflow

## [1.0.0] - 2024-06-07

### Added
- **Initial TFT-Moonraker bridge implementation**
  - Basic G-code translation between TFT and Klipper
  - Serial communication handling for TFT devices
  - Moonraker API integration
  - Support for common 3D printer commands
- **Core functionality**
  - Temperature monitoring (M105, M115)
  - Movement commands (G0, G1, G28)
  - Bed leveling translation (G29, M420, M421)
  - Filament handling (M701, M702)
  - Print control commands
- **Installation and setup scripts**
  - Interactive installer with configuration wizard
  - Simple setup script for automated deployment
  - Systemd service integration
  - Klipper macro compatibility system

### Features
- Real-time G-code translation
- Automatic macro detection and integration
- Comprehensive documentation
- Production-ready systemd service
- Compatible with existing Klipper setups

---

## Version Numbering

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

## Upgrade Notes

### From 2.1.x to 2.2.x
- **Fully compatible**: No breaking changes
- Enhanced standalone script with better user experience
- New dependency management improves installation reliability
- Existing installations continue to work without changes
- Consider using `requirements.txt` for future dependency management

### From 2.0.x to 2.1.x
- **Fully compatible**: No breaking changes
- New features are opt-in (standalone mode, test mode)
- Existing installations continue to work without changes

### From 1.x to 2.x
- **Breaking changes**: See 2.0.0 changelog
- Requires `aiohttp` dependency installation
- Configuration may need updates for new validation

## Support

For issues, feature requests, or questions:
- Check the documentation in the `tftKlipperBridge/` folder
- Review compatibility guides for your specific setup
- Test new versions safely using `--test-mode` flag