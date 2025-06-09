#!/usr/bin/env python3
"""
TFT Moonraker Bridge - Production Version
Translates TFT G-codes to Moonraker API calls with enhanced error handling and security

This script acts as a bridge between BigTreeTech TFT touchscreens and Klipper via Moonraker.
Features comprehensive error handling, security validation, automatic reconnection, and
production-grade robustness for 24/7 operation.

Author: Claude Code
License: GPL-3.0
Version: 2.2.0
"""

# Version information
__version__ = "2.3.4"
__build_date__ = "2025-06-09"
__git_hash__ = "initial"
__author__ = "Claude Code"
__license__ = "GPL-3.0"

# Version history
VERSION_HISTORY = {
    "2.3.4": {
        "date": "2025-06-09",
        "features": [
            "Reorganized installation to use proper subfolder structure",
            "Installation now uses ~/tft-klipper-bridge/ instead of cluttering home directory",
            "Updated all scripts to support new directory structure",
            "Backward compatibility with existing installations",
            "Enhanced uninstall script to handle both old and new locations"
        ],
        "breaking_changes": []
    },
    "2.3.3": {
        "date": "2025-06-09",
        "features": [
            "Added comprehensive uninstall script (uninstall_tft_bridge.sh)",
            "Safe removal with optional component deletion prompts",
            "Automatic service cleanup and verification",
            "Updated documentation with uninstall instructions",
            "Enhanced project maintenance and cleanup capabilities"
        ],
        "breaking_changes": []
    },
    "2.3.2": {
        "date": "2025-06-09",
        "features": [
            "Fixed Klipper macro file syntax error preventing configuration loading",
            "Removed invalid top-level Jinja2 conditionals from macro file",
            "Restructured macro definitions to use proper Klipper format",
            "Maintained smart macro compatibility logic within macro definitions"
        ],
        "breaking_changes": []
    },
    "2.3.1": {
        "date": "2025-06-09",
        "features": [
            "Fixed externally-managed-environment pip installation errors",
            "Added support for virtual environments in installation scripts",
            "Enhanced dependency installation with multiple fallback methods",
            "Improved system package manager support (apt, dnf, pacman)",
            "Added comprehensive installation troubleshooting guides"
        ],
        "breaking_changes": []
    },
    "2.3.0": {
        "date": "2025-06-09",
        "features": [
            "Added comprehensive CLAUDE.md documentation for development guidance",
            "Prepared codebase for open source release with git repository setup",
            "Updated version management and build information",
            "Enhanced development workflow documentation"
        ],
        "breaking_changes": []
    },
    "2.2.0": {
        "date": "2024-06-09",
        "features": [
            "Enhanced standalone script with interactive serial port setup",
            "Added comprehensive dependency management (requirements.txt)",
            "Implemented smart port detection with device information",
            "Added permission validation and helpful error messages",
            "Created professional installation documentation",
            "Multiple installation methods with full automation support"
        ],
        "breaking_changes": []
    },
    "2.1.0": {
        "date": "2024-06-09",
        "features": [
            "Added comprehensive version handling",
            "Implemented standalone mode for zero-setup operation",
            "Enhanced connection resilience (never stops on failures)",
            "Added test mode for safe testing",
            "Improved error handling and recovery"
        ],
        "breaking_changes": []
    },
    "2.0.0": {
        "date": "2024-06-08", 
        "features": [
            "Complete robustness overhaul",
            "Added security validation and input sanitization",
            "Implemented async HTTP with connection pooling",
            "Added rate limiting and resource management",
            "Enhanced error handling with retry logic"
        ],
        "breaking_changes": [
            "Replaced synchronous HTTP with async aiohttp",
            "Changed configuration validation"
        ]
    },
    "1.0.0": {
        "date": "2024-06-07",
        "features": [
            "Initial TFT-Moonraker bridge implementation",
            "Basic G-code translation",
            "Serial communication handling",
            "Moonraker API integration"
        ],
        "breaking_changes": []
    }
}

import sys
import argparse
import serial
import asyncio
import aiohttp
import json
import re
import logging
import time
import os
import signal
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass
from urllib.parse import urljoin
from collections import deque
import socket


def get_version_info():
    """Get comprehensive version information"""
    return {
        "version": __version__,
        "build_date": __build_date__,
        "git_hash": __git_hash__,
        "author": __author__,
        "license": __license__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform
    }


def print_version_info():
    """Print formatted version information"""
    info = get_version_info()
    print(f"TFT-Moonraker Bridge v{info['version']}")
    print(f"Build: {info['build_date']} ({info['git_hash']})")
    print(f"Author: {info['author']}")
    print(f"License: {info['license']}")
    print(f"Python: {info['python_version']} on {info['platform']}")


def print_version_history(version=None):
    """Print version history or specific version changelog"""
    if version:
        if version in VERSION_HISTORY:
            v = VERSION_HISTORY[version]
            print(f"\n=== Version {version} ({v['date']}) ===")
            print("\nFeatures:")
            for feature in v['features']:
                print(f"  + {feature}")
            if v['breaking_changes']:
                print("\nBreaking Changes:")
                for change in v['breaking_changes']:
                    print(f"  ! {change}")
        else:
            print(f"Version {version} not found in history")
            print(f"Available versions: {', '.join(VERSION_HISTORY.keys())}")
    else:
        print("=== TFT Bridge Version History ===")
        for ver, info in sorted(VERSION_HISTORY.items(), key=lambda x: x[0], reverse=True):
            print(f"\nv{ver} ({info['date']}):")
            for feature in info['features'][:2]:  # Show first 2 features
                print(f"  + {feature}")
            if len(info['features']) > 2:
                print(f"  + ... and {len(info['features']) - 2} more")


def check_version_compatibility():
    """Check Python version compatibility"""
    min_version = (3, 7)
    current = sys.version_info[:2]
    
    if current < min_version:
        print(f"⚠ Warning: Python {current[0]}.{current[1]} detected")
        print(f"Minimum required: Python {min_version[0]}.{min_version[1]}")
        print("Some features may not work correctly")
        return False
    return True




@dataclass
class BridgeConfig:
    """Configuration for the TFT-Moonraker bridge with validation"""
    serial_port: str
    baud_rate: int
    moonraker_host: str = "localhost"
    moonraker_port: int = 7125
    log_level: str = "INFO"
    timeout: float = 5.0
    max_retries: int = 5
    retry_delay: float = 1.0
    test_mode: bool = False
    standalone_mode: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()
    
    def validate(self):
        """Validate all configuration parameters"""
        # In standalone mode, be more permissive
        if self.standalone_mode:
            # Only validate critical parameters
            if self.timeout <= 0:
                self.timeout = 5.0
            if self.max_retries < 0:
                self.max_retries = 5
            if self.retry_delay < 0:
                self.retry_delay = 1.0
            return
        
        # Validate serial port
        if not self.serial_port:
            raise ValueError("Serial port cannot be empty")
        
        # Validate baud rate
        valid_baud_rates = [9600, 19200, 38400, 57600, 115200, 230400, 250000, 460800, 921600]
        if self.baud_rate not in valid_baud_rates:
            raise ValueError(f"Invalid baud rate: {self.baud_rate}. Must be one of {valid_baud_rates}")
        
        # Validate host
        if not self.moonraker_host:
            raise ValueError("Moonraker host cannot be empty")
        
        # Validate port
        if not (1 <= self.moonraker_port <= 65535):
            raise ValueError(f"Invalid port: {self.moonraker_port}. Must be 1-65535")
        
        # Validate timeout
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        # Validate retry parameters
        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")
        
        if self.retry_delay < 0:
            raise ValueError("Retry delay must be non-negative")


class SecurityValidator:
    """Validates and sanitizes inputs for security"""
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate filename to prevent path traversal attacks"""
        if not filename:
            return False
        
        # Check for path traversal attempts
        if '..' in filename or filename.startswith('/') or '\\' in filename:
            return False
        
        # Check for absolute paths
        if os.path.isabs(filename):
            return False
        
        # Check filename length
        if len(filename) > 255:
            return False
        
        return True
    
    @staticmethod
    def sanitize_gcode(gcode: str) -> str:
        """Sanitize G-code to prevent command injection"""
        if not gcode:
            return ""
        
        # Remove dangerous characters but preserve valid G-code syntax
        # Allow letters, numbers, spaces, dots, dashes, plus, equals, colons
        sanitized = re.sub(r'[^\w\s\.\-\+\=\:]', '', gcode.strip())
        
        # Limit length to prevent buffer overflow
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
        
        return sanitized


class RateLimiter:
    """Rate limiter to prevent API flooding"""
    
    def __init__(self, max_requests: int = 10, time_window: float = 1.0):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request"""
        async with self._lock:
            now = time.time()
            
            # Remove old requests outside time window
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()
            
            # If we're at the limit, wait
            if len(self.requests) >= self.max_requests:
                sleep_time = self.time_window - (now - self.requests[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    # Remove the old request after waiting
                    if self.requests:
                        self.requests.popleft()
            
            self.requests.append(now)


class ConnectionManager:
    """Manages connections with automatic reconnection"""
    
    def __init__(self, config: BridgeConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        self.connected = False
        self.reconnect_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the connection manager"""
        await self.create_session()
        self.reconnect_task = asyncio.create_task(self._reconnect_loop())
    
    async def stop(self):
        """Stop the connection manager and cleanup"""
        if self.reconnect_task:
            self.reconnect_task.cancel()
            try:
                await self.reconnect_task
            except asyncio.CancelledError:
                pass
        
        await self.cleanup()
    
    async def create_session(self):
        """Create HTTP session with proper configuration"""
        if self.session and not self.session.closed:
            await self.session.close()
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
    
    async def connect_websocket(self):
        """Connect to Moonraker websocket with retry logic"""
        for attempt in range(self.config.max_retries):
            try:
                if not self.session or self.session.closed:
                    await self.create_session()
                
                ws_url = f"ws://{self.config.moonraker_host}:{self.config.moonraker_port}/websocket"
                self.websocket = await self.session.ws_connect(ws_url)
                self.connected = True
                self.logger.info("Connected to Moonraker websocket")
                return True
                
            except Exception as e:
                self.logger.warning(f"Websocket connection attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
        
        self.connected = False
        return False
    
    async def _reconnect_loop(self):
        """Background task to maintain websocket connection"""
        while True:
            try:
                if not self.connected or (self.websocket and self.websocket.closed):
                    self.logger.info("Attempting to reconnect websocket...")
                    await self.connect_websocket()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Reconnection loop error: {e}")
                await asyncio.sleep(5)
    
    async def cleanup(self):
        """Cleanup all connections"""
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
        
        if self.session and not self.session.closed:
            await self.session.close()
        
        self.connected = False


class TestModeHandler:
    """Handles test mode operations safely"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.command_count = 0
        self.start_time = time.time()
        
    def log_command(self, gcode: str, translated: str = None):
        """Log commands in test mode"""
        self.command_count += 1
        if translated:
            self.logger.info(f"[TEST] Command #{self.command_count}: '{gcode}' -> '{translated}' (NOT EXECUTED)")
        else:
            self.logger.info(f"[TEST] Command #{self.command_count}: '{gcode}' (local command)")
    
    def get_stats(self):
        """Get test mode statistics"""
        runtime = time.time() - self.start_time
        return {
            "commands_processed": self.command_count,
            "runtime_seconds": runtime,
            "commands_per_minute": (self.command_count / runtime * 60) if runtime > 0 else 0
        }


class MoonrakerClient:
    """Handles communication with Moonraker API with enhanced robustness"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.base_url = f"http://{config.moonraker_host}:{config.moonraker_port}"
        self.logger = logging.getLogger("MoonrakerClient")
        self.connection_manager = ConnectionManager(config, self.logger)
        self.rate_limiter = RateLimiter(max_requests=20, time_window=1.0)
        self.validator = SecurityValidator()
        self.test_handler = TestModeHandler(self.logger) if config.test_mode else None
        
        if config.test_mode:
            self.logger.warning("🧪 TEST MODE ENABLED - Commands will NOT be executed on printer!")
    
    async def start(self):
        """Start the Moonraker client"""
        await self.connection_manager.start()
        
        # Test initial connection
        try:
            await self.get_printer_info()
            self.logger.info("Successfully connected to Moonraker API")
        except Exception as e:
            if self.config.test_mode:
                self.logger.info("🧪 Test mode: Moonraker connection not required")
            else:
                self.logger.warning(f"Initial Moonraker connection test failed: {e}")
                self.logger.warning(f"Moonraker URL: {self.base_url}")
                self.logger.warning("Please ensure:")
                self.logger.warning("  • Klipper and Moonraker are running")
                self.logger.warning("  • Moonraker is accessible at the configured host:port")
                self.logger.warning("  • No firewall blocking the connection")
                self.logger.warning("Bridge will continue and retry connections automatically")
    
    async def stop(self):
        """Stop the Moonraker client"""
        await self.connection_manager.stop()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with retry logic and rate limiting"""
        await self.rate_limiter.acquire()
        
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(self.config.max_retries):
            try:
                if not self.connection_manager.session or self.connection_manager.session.closed:
                    await self.connection_manager.create_session()
                
                session = self.connection_manager.session
                
                if method.upper() == 'GET':
                    async with session.get(url) as response:
                        response.raise_for_status()
                        return await response.json()
                elif method.upper() == 'POST':
                    async with session.post(url, json=data) as response:
                        response.raise_for_status()
                        return await response.json()
                        
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                error_msg = f"Request attempt {attempt + 1} failed: {e}"
                if attempt == 0:  # First attempt, provide helpful context
                    if "Connection refused" in str(e) or "Cannot connect" in str(e):
                        error_msg += f" (Moonraker may not be running on {self.config.moonraker_host}:{self.config.moonraker_port})"
                    elif "Timeout" in str(e):
                        error_msg += " (Request timeout - check network connectivity)"
                    elif "Server disconnected" in str(e):
                        error_msg += " (Moonraker closed connection - may be overloaded or restarting)"
                
                self.logger.warning(error_msg)
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error in request: {e}")
                raise
        
        return {"error": "Max retries exceeded"}
    
    async def send_gcode(self, gcode: str) -> Dict[str, Any]:
        """Send G-code to Klipper via Moonraker with validation"""
        try:
            # Sanitize the G-code
            sanitized_gcode = self.validator.sanitize_gcode(gcode)
            if not sanitized_gcode:
                return {"error": "Invalid or empty G-code"}
            
            if sanitized_gcode != gcode:
                self.logger.warning(f"G-code was sanitized: '{gcode}' -> '{sanitized_gcode}'")
            
            # Test mode - don't actually send commands
            if self.config.test_mode:
                self.test_handler.log_command(gcode, sanitized_gcode)
                return {"result": "ok", "test_mode": True}
            
            data = {"script": sanitized_gcode}
            return await self._make_request("POST", "/printer/gcode/script", data)
            
        except Exception as e:
            self.logger.error(f"Failed to send G-code '{gcode}': {e}")
            return {"error": str(e)}
    
    async def get_printer_status(self) -> Dict[str, Any]:
        """Get current printer status"""
        try:
            # Test mode - return fake temperature data
            if self.config.test_mode:
                return {
                    "result": {
                        "status": {
                            "extruder": {"temperature": 25.0, "target": 0.0},
                            "heater_bed": {"temperature": 24.0, "target": 0.0}
                        }
                    },
                    "test_mode": True
                }
            
            endpoint = "/printer/objects/query?extruder&heater_bed&fan&toolhead&print_stats"
            return await self._make_request("GET", endpoint)
        except Exception as e:
            self.logger.error(f"Failed to get printer status: {e}")
            return {"error": str(e)}
    
    async def get_printer_info(self) -> Dict[str, Any]:
        """Get printer information for connection testing"""
        try:
            return await self._make_request("GET", "/printer/info")
        except Exception as e:
            self.logger.error(f"Failed to get printer info: {e}")
            return {"error": str(e)}
    
    async def start_print(self, filename: str) -> Dict[str, Any]:
        """Start a print job with filename validation"""
        try:
            if not self.validator.validate_filename(filename):
                return {"error": "Invalid filename - potential security risk"}
            
            data = {"filename": filename}
            return await self._make_request("POST", "/printer/print/start", data)
        except Exception as e:
            self.logger.error(f"Failed to start print: {e}")
            return {"error": str(e)}
    
    async def pause_print(self) -> Dict[str, Any]:
        """Pause current print"""
        try:
            return await self._make_request("POST", "/printer/print/pause")
        except Exception as e:
            self.logger.error(f"Failed to pause print: {e}")
            return {"error": str(e)}
    
    async def resume_print(self) -> Dict[str, Any]:
        """Resume paused print"""
        try:
            return await self._make_request("POST", "/printer/print/resume")
        except Exception as e:
            self.logger.error(f"Failed to resume print: {e}")
            return {"error": str(e)}
    
    async def cancel_print(self) -> Dict[str, Any]:
        """Cancel current print"""
        try:
            return await self._make_request("POST", "/printer/print/cancel")
        except Exception as e:
            self.logger.error(f"Failed to cancel print: {e}")
            return {"error": str(e)}


class GCodeTranslator:
    """Translates TFT G-codes to Moonraker API calls or Klipper macros"""
    
    def __init__(self, moonraker_client: MoonrakerClient):
        self.moonraker = moonraker_client
        self.logger = logging.getLogger("GCodeTranslator")
        self.available_macros: Set[str] = set()
        self.macros_checked = False
        self._macro_check_lock = asyncio.Lock()
        
        # Translation mapping
        self.translations = {
            # Bed leveling commands
            r"M420\s+S1": "BED_MESH_PROFILE LOAD=default",
            r"M420\s+S0": "BED_MESH_CLEAR",
            r"G29": "BED_MESH_CALIBRATE",
            r"M421\s+I(\d+)\s+J(\d+)\s+Z([+-]?\d*\.?\d+)": lambda m: f"BED_MESH_CALIBRATE MESH_MIN={m.group(1)},{m.group(2)} MESH_MAX={m.group(1)},{m.group(2)}",
            
            # PID tuning
            r"M303\s+E0\s+C8\s+U1": "PID_CALIBRATE HEATER=extruder",
            r"M303\s+E-1\s+C8\s+U1": "PID_CALIBRATE HEATER=heater_bed",
            
            # BLTouch/Probe commands
            r"M280\s+P0\s+S10": "BLTOUCH_DEBUG COMMAND=pin_down",
            r"M280\s+P0\s+S90": "BLTOUCH_DEBUG COMMAND=pin_up", 
            r"M280\s+P0\s+S160": "BLTOUCH_DEBUG COMMAND=reset",
            r"M401": "PROBE_CALIBRATE",
            r"M48": "PROBE_ACCURACY",
            
            # Filament handling - will use existing macros if available
            r"M701": "LOAD_FILAMENT",
            r"M702": "UNLOAD_FILAMENT",
            
            # Settings (translate to dummy responses since Klipper uses config files)
            r"M500": "SAVE_CONFIG",
            r"M503": "# Settings saved in printer.cfg",
            
            # Z-offset
            r"M851\s+Z([+-]?\d*\.?\d+)": lambda m: f"SET_GCODE_OFFSET Z={m.group(1)} MOVE=1",
        }
    
    async def check_available_macros(self):
        """Check what macros are available in Klipper with thread safety"""
        if self.macros_checked:
            return
        
        async with self._macro_check_lock:
            if self.macros_checked:  # Double-check pattern
                return
            
            try:
                endpoint = "/printer/objects/query?configfile"
                result = await self.moonraker._make_request("GET", endpoint)
                
                if "result" in result and "status" in result["result"] and "configfile" in result["result"]["status"]:
                    config = result["result"]["status"]["configfile"]["settings"]
                    
                    # Find all gcode_macro entries
                    for key in config.keys():
                        if key.startswith("gcode_macro "):
                            macro_name = key.replace("gcode_macro ", "").upper()
                            self.available_macros.add(macro_name)
                            
                    self.logger.info(f"Found {len(self.available_macros)} available macros")
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(f"Available macros: {sorted(self.available_macros)}")
                    
                    # Always show important filament macros if found
                    important_macros = ["LOAD_FILAMENT", "UNLOAD_FILAMENT", "PAUSE", "RESUME", "CANCEL_PRINT"]
                    found_important = [macro for macro in important_macros if macro in self.available_macros]
                    if found_important:
                        self.logger.info(f"Important macros detected: {', '.join(found_important)}")
                    
            except Exception as e:
                self.logger.warning(f"Could not check available macros: {e}")
            finally:
                self.macros_checked = True
    
    def list_all_macros(self):
        """List all available macros"""
        if not self.macros_checked:
            self.logger.warning("Macros not yet checked. Run bridge first to detect macros.")
            return
        
        if not self.available_macros:
            self.logger.info("No G-code macros found in Klipper configuration")
            return
        
        self.logger.info("=" * 50)
        self.logger.info(f"KLIPPER MACROS DETECTED ({len(self.available_macros)} total)")
        self.logger.info("=" * 50)
        
        # Group macros by category for better readability
        categories = {
            "Filament": ["LOAD_FILAMENT", "UNLOAD_FILAMENT", "CHANGE_FILAMENT"],
            "Print Control": ["PAUSE", "RESUME", "CANCEL_PRINT", "START_PRINT", "END_PRINT"],
            "Bed Leveling": ["BED_MESH_CALIBRATE", "BED_MESH_LOAD", "BED_MESH_SAVE", "Z_TILT_ADJUST", "SCREWS_TILT_CALCULATE"],
            "Probe/BLTouch": ["PROBE_CALIBRATE", "PROBE_ACCURACY", "BLTOUCH_DEBUG", "BLTOUCH_STORE"],
            "Maintenance": ["CLEAN_NOZZLE", "PURGE_NOZZLE", "HEAT_SOAK", "PARK"],
            "Custom": []
        }
        
        # Categorize macros
        categorized = {cat: [] for cat in categories}
        uncategorized = set(self.available_macros)
        
        for category, macro_list in categories.items():
            if category == "Custom":
                continue
            for macro in macro_list:
                if macro in self.available_macros:
                    categorized[category].append(macro)
                    uncategorized.discard(macro)
        
        # Add remaining macros to Custom
        categorized["Custom"] = sorted(uncategorized)
        
        # Display by category
        for category, macros in categorized.items():
            if macros:
                self.logger.info(f"\n{category}:")
                for macro in sorted(macros):
                    self.logger.info(f"  • {macro}")
        
        self.logger.info("=" * 50)
    
    async def translate_gcode(self, gcode: str) -> Optional[str]:
        """Translate a G-code command to Klipper equivalent"""
        if not gcode or not gcode.strip():
            return None
        
        gcode = gcode.strip()
        
        # Check available macros if we haven't already
        await self.check_available_macros()
        
        # Special handling for filament commands if user has existing macros
        if gcode.upper() == "M701":
            if "LOAD_FILAMENT" in self.available_macros:
                self.logger.debug("Using existing LOAD_FILAMENT macro")
                return "LOAD_FILAMENT"
            else:
                self.logger.warning("No LOAD_FILAMENT macro found, using fallback")
                return "TFT_LOAD_FILAMENT"
                
        if gcode.upper() == "M702":
            if "UNLOAD_FILAMENT" in self.available_macros:
                self.logger.debug("Using existing UNLOAD_FILAMENT macro")
                return "UNLOAD_FILAMENT"
            else:
                self.logger.warning("No UNLOAD_FILAMENT macro found, using fallback")
                return "TFT_UNLOAD_FILAMENT"
        
        # Check for direct translations
        for pattern, replacement in self.translations.items():
            try:
                match = re.match(pattern, gcode, re.IGNORECASE)
                if match:
                    if callable(replacement):
                        return replacement(match)
                    else:
                        return replacement
            except Exception as e:
                self.logger.error(f"Error processing translation pattern {pattern}: {e}")
                continue
                    
        # Pass through standard G-codes that work in Klipper
        passthrough_patterns = [
            r"G[01]\s+.*",  # Movement commands
            r"G28.*",       # Homing
            r"G9[01]",      # Positioning modes
            r"G92.*",       # Set position
            r"M10[4-9].*",  # Temperature commands
            r"M11[45].*",   # M114 (position), M115 (firmware info)
            r"M1[89]0.*",   # Bed temperature
            r"M220.*",      # Speed factor
            r"M221.*",      # Flow factor
            r"M[23][0-9].*" # Print control
        ]
        
        for pattern in passthrough_patterns:
            try:
                if re.match(pattern, gcode, re.IGNORECASE):
                    return gcode
            except Exception as e:
                self.logger.error(f"Error checking passthrough pattern {pattern}: {e}")
                continue
                
        # Commands that need special handling
        if gcode.upper().startswith("M115"):
            return None  # Will be handled specially
        elif gcode.upper().startswith("M105"):
            return None  # Temperature reporting handled specially
            
        self.logger.debug(f"No translation found for: {gcode}")
        return None


class TFTSerial:
    """Handles serial communication with TFT with enhanced error handling"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.serial: Optional[serial.Serial] = None
        self.logger = logging.getLogger("TFTSerial")
        self.connected = False
        self._read_buffer = ""
    
    async def connect(self) -> bool:
        """Connect to TFT serial port with validation"""
        try:
            # In standalone mode, don't fail if serial port doesn't exist
            if not os.path.exists(self.config.serial_port):
                if self.config.standalone_mode:
                    self.logger.warning(f"Serial port {self.config.serial_port} does not exist (standalone mode)")
                    return False
                else:
                    self.logger.error(f"Serial port {self.config.serial_port} does not exist")
                    return False
            
            # Check if port is accessible
            try:
                test_serial = serial.Serial(self.config.serial_port, timeout=0.1)
                test_serial.close()
            except serial.SerialException as e:
                self.logger.error(f"Cannot access serial port {self.config.serial_port}: {e}")
                return False
            
            self.serial = serial.Serial(
                port=self.config.serial_port,
                baudrate=self.config.baud_rate,
                timeout=1.0,
                write_timeout=1.0,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            self.connected = True
            self.logger.info(f"Connected to TFT on {self.config.serial_port} at {self.config.baud_rate} baud")
            return True
            
        except serial.SerialException as e:
            self.logger.error(f"Serial connection failed: {e}")
            self.connected = False
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to TFT: {e}")
            self.connected = False
            return False
    
    async def read_line(self) -> Optional[str]:
        """Read a line from TFT with improved buffering"""
        if not self.connected or not self.serial:
            return None
        
        try:
            # Check for data availability
            if self.serial.in_waiting == 0:
                return None
            
            # Read available data
            data = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
            self._read_buffer += data
            
            # Extract complete lines
            if '\n' in self._read_buffer:
                lines = self._read_buffer.split('\n')
                self._read_buffer = lines[-1]  # Keep incomplete line in buffer
                
                # Return the first complete line
                if lines[0].strip():
                    return lines[0].strip()
            
        except serial.SerialException as e:
            self.logger.error(f"Serial read error: {e}")
            self.connected = False
        except UnicodeDecodeError as e:
            self.logger.warning(f"Unicode decode error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error reading from TFT: {e}")
        
        return None
    
    async def write_line(self, data: str):
        """Write a line to TFT with error handling"""
        if not self.connected or not self.serial:
            return False
        
        try:
            # Validate data length
            if len(data) > 1000:
                self.logger.warning(f"Data too long, truncating: {data[:50]}...")
                data = data[:1000]
            
            line = f"{data}\n"
            self.serial.write(line.encode('utf-8'))
            self.serial.flush()
            return True
            
        except serial.SerialException as e:
            self.logger.error(f"Serial write error: {e}")
            self.connected = False
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error writing to TFT: {e}")
            return False
    
    def close(self):
        """Close serial connection"""
        self.connected = False
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
                self.logger.info("Serial connection closed")
            except Exception as e:
                self.logger.error(f"Error closing serial connection: {e}")


class TFTMoonrakerBridge:
    """Main bridge class with enhanced robustness"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.logger = logging.getLogger("TFTBridge")
        
        if config.test_mode:
            self.logger.warning("🧪 TEST MODE ENABLED - Bridge will simulate operations without affecting printer")
        
        if config.standalone_mode:
            self.logger.warning("🚀 STANDALONE MODE - Running without installation, minimal setup required")
        
        self.tft = TFTSerial(config)
        self.moonraker = MoonrakerClient(config)
        self.translator = GCodeTranslator(self.moonraker)
        
        self.running = False
        self.last_temp_report = 0
        self.temp_report_interval = 2.0
        self.shutdown_event = asyncio.Event()
        
        # Setup signal handlers
        for sig in [signal.SIGTERM, signal.SIGINT]:
            signal.signal(sig, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False
        self.shutdown_event.set()
    
    async def handle_m115(self):
        """Handle M115 firmware info request"""
        try:
            # Include bridge version in firmware response
            response = f"FIRMWARE_NAME:Klipper FIRMWARE_VERSION:v0.11.0 PROTOCOL_VERSION:1.0 MACHINE_TYPE:TFT_Bridge BRIDGE_VERSION:{__version__}"
            await self.tft.write_line(response)
            await self.tft.write_line("ok")
        except Exception as e:
            self.logger.error(f"Error handling M115: {e}")
    
    async def handle_m105(self):
        """Handle M105 temperature reporting"""
        try:
            status = await self.moonraker.get_printer_status()
            if "result" in status and "status" in status["result"]:
                printer_status = status["result"]["status"]
                
                # Format temperature response like Marlin
                temp_parts = []
                
                if "extruder" in printer_status:
                    ext = printer_status["extruder"]
                    temp_parts.append(f"T:{ext.get('temperature', 0):.1f} /{ext.get('target', 0):.1f}")
                    
                if "heater_bed" in printer_status:
                    bed = printer_status["heater_bed"]
                    temp_parts.append(f"B:{bed.get('temperature', 0):.1f} /{bed.get('target', 0):.1f}")
                    
                response = "ok " + " ".join(temp_parts) if temp_parts else "ok T:0.0 /0.0 B:0.0 /0.0"
                await self.tft.write_line(response)
            else:
                await self.tft.write_line("ok T:0.0 /0.0 B:0.0 /0.0")
                
        except Exception as e:
            # Moonraker unavailable - provide fallback temperature response
            self.logger.debug(f"Moonraker unavailable for temperature request: {e}")
            await self.tft.write_line("ok T:0.0 /0.0 B:0.0 /0.0")
    
    async def send_periodic_updates(self):
        """Send periodic temperature updates to TFT"""
        while self.running:
            try:
                # Only send updates if TFT is connected
                if self.tft.connected:
                    current_time = time.time()
                    if current_time - self.last_temp_report >= self.temp_report_interval:
                        await self.handle_m105()
                        self.last_temp_report = current_time
                
                await asyncio.sleep(0.5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic updates: {e}")
                await asyncio.sleep(1.0)
    
    async def tft_connection_monitor(self):
        """Monitor and maintain TFT connection"""
        tft_retry_delay = 5.0  # Start with 5 second delay
        max_retry_delay = 60.0  # Maximum 1 minute delay
        
        while self.running:
            try:
                if not self.tft.connected:
                    self.logger.info(f"TFT not connected, attempting connection in {tft_retry_delay}s...")
                    await asyncio.sleep(tft_retry_delay)
                    
                    if await self.tft.connect():
                        self.logger.info("TFT connection restored")
                        tft_retry_delay = 5.0  # Reset delay on successful connection
                    else:
                        # Exponential backoff for failed connections
                        tft_retry_delay = min(tft_retry_delay * 1.5, max_retry_delay)
                        self.logger.warning(f"TFT connection failed, next attempt in {tft_retry_delay}s")
                else:
                    # TFT is connected, check every 10 seconds
                    await asyncio.sleep(10.0)
                    tft_retry_delay = 5.0  # Reset delay when connected
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in TFT connection monitor: {e}")
                await asyncio.sleep(5.0)
    
    async def process_gcode(self, gcode: str):
        """Process a G-code from TFT"""
        try:
            gcode = gcode.strip()
            if not gcode:
                return
            
            self.logger.debug(f"Received: {gcode}")
            
            # Handle special commands locally (no Moonraker needed)
            if gcode.upper().startswith("M115"):
                if self.config.test_mode:
                    self.moonraker.test_handler.log_command(gcode)
                await self.handle_m115()
                return
            elif gcode.upper().startswith("M105"):
                if self.config.test_mode:
                    self.moonraker.test_handler.log_command(gcode)
                await self.handle_m105()
                return
            
            # Translate G-code
            translated = await self.translator.translate_gcode(gcode)
            
            if translated:
                self.logger.info(f"Translating '{gcode}' -> '{translated}'")
                
                try:
                    result = await self.moonraker.send_gcode(translated)
                    
                    if "error" in result:
                        self.logger.warning(f"Moonraker error for '{gcode}': {result['error']}")
                        await self.tft.write_line(f"!! {result['error']}")
                    else:
                        await self.tft.write_line("ok")
                        
                except Exception as moonraker_error:
                    # Moonraker is unavailable, but don't crash - just log and respond
                    self.logger.warning(f"Moonraker unavailable for '{gcode}': {moonraker_error}")
                    await self.tft.write_line("ok")  # Keep TFT happy even if Moonraker fails
            else:
                # Unknown command, send ok to keep TFT happy
                self.logger.debug(f"Unknown command: {gcode}")
                await self.tft.write_line("ok")
                
        except Exception as e:
            self.logger.error(f"Error processing G-code '{gcode}': {e}")
            # Always try to respond to TFT, even if something goes wrong
            try:
                await self.tft.write_line("ok")
            except:
                pass  # Don't crash if TFT write fails too
    
    async def run(self) -> bool:
        """Main bridge loop with comprehensive error handling"""
        self.logger.info(f"Starting TFT-Moonraker Bridge v{__version__}")
        self.logger.info(f"Build: {__build_date__} | Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        self.logger.info(f"Moonraker: {self.config.moonraker_host}:{self.config.moonraker_port}")
        self.logger.info(f"Serial: {self.config.serial_port} @ {self.config.baud_rate} baud")
        
        if not self.config.test_mode:
            self.logger.info("💡 Tip: Use --test-mode flag first to verify setup without affecting printer")
        
        try:
            # Start Moonraker client (non-blocking)
            await self.moonraker.start()
            
            # Start bridge even if TFT not initially connected
            self.running = True
            self.logger.info("Bridge started - will connect to devices as they become available")
            
            # Start background tasks
            tasks = []
            tasks.append(asyncio.create_task(self.send_periodic_updates()))
            tasks.append(asyncio.create_task(self.tft_connection_monitor()))
            
            # Main processing loop
            try:
                while self.running:
                    # Check for shutdown
                    if self.shutdown_event.is_set():
                        break
                    
                    # Only process if TFT is connected
                    if self.tft.connected:
                        # Read from TFT
                        line = await self.tft.read_line()
                        if line:
                            await self.process_gcode(line)
                    
                    await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning
                    
            except asyncio.CancelledError:
                self.logger.info("Bridge loop cancelled")
            except Exception as e:
                self.logger.error(f"Bridge loop error: {e}")
            finally:
                # Cancel background tasks
                for task in tasks:
                    task.cancel()
                
                # Wait for tasks to complete
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Cleanup
                await self.cleanup()
        
        except Exception as e:
            self.logger.error(f"Fatal bridge error: {e}")
            return False
        
        self.logger.info("Bridge shutdown complete")
        return True
    
    async def cleanup(self):
        """Comprehensive cleanup procedure"""
        self.logger.info("Starting cleanup...")
        
        try:
            self.running = False
            
            # Print test mode statistics if in test mode
            if self.config.test_mode and self.moonraker.test_handler:
                stats = self.moonraker.test_handler.get_stats()
                self.logger.info("🧪 TEST MODE STATISTICS:")
                self.logger.info(f"   Commands processed: {stats['commands_processed']}")
                self.logger.info(f"   Runtime: {stats['runtime_seconds']:.1f} seconds")
                self.logger.info(f"   Commands per minute: {stats['commands_per_minute']:.1f}")
            
            # Close TFT connection
            self.tft.close()
            
            # Stop Moonraker client
            await self.moonraker.stop()
            
            self.logger.info("Cleanup complete")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def setup_logging(level: str, log_file: str = "tft_bridge.log"):
    """Setup logging with rotation and security considerations"""
    import logging.handlers
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        root_logger.warning(f"Could not setup file logging: {e}")


async def main():
    """Main entry point with comprehensive error handling"""
    parser = argparse.ArgumentParser(description="TFT-Moonraker Bridge (Production Version)")
    parser.add_argument("--serial-port", "-p", 
                       help="Serial port for TFT (e.g., /dev/ttyUSB0)")
    parser.add_argument("--baud-rate", "-b", type=int, default=250000,
                       help="Baud rate for TFT communication (default: 250000)")
    parser.add_argument("--moonraker-host", "-m", default="localhost",
                       help="Moonraker host (default: localhost)")
    parser.add_argument("--moonraker-port", "-P", type=int, default=7125,
                       help="Moonraker port (default: 7125)")
    parser.add_argument("--log-level", "-l", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Log level (default: INFO)")
    parser.add_argument("--timeout", "-t", type=float, default=5.0,
                       help="Request timeout in seconds (default: 5.0)")
    parser.add_argument("--max-retries", "-r", type=int, default=5,
                       help="Maximum retry attempts (default: 5)")
    parser.add_argument("--log-file", "-f", default="tft_bridge.log",
                       help="Log file path (default: tft_bridge.log)")
    parser.add_argument("--test-mode", "-T", action="store_true",
                       help="🧪 Enable test mode - commands will be logged but NOT executed on printer")
    parser.add_argument("--standalone", "-S", action="store_true",
                       help="🚀 Standalone mode - run without installation or setup")
    parser.add_argument("--version", "-V", action="store_true",
                       help="Show version information and exit")
    parser.add_argument("--version-history", action="store_true",
                       help="Show version history and exit")
    parser.add_argument("--version-info", metavar="VERSION",
                       help="Show detailed info for specific version")
    parser.add_argument("--list-macros", action="store_true",
                       help="Connect to Moonraker and list all detected G-code macros")
    
    args = parser.parse_args()
    
    # Handle version commands first
    if args.version:
        print_version_info()
        return 0
    
    if args.version_history:
        print_version_history()
        return 0
    
    if args.version_info:
        print_version_history(args.version_info)
        return 0
    
    # Handle macro listing
    if args.list_macros:
        # Setup minimal logging for macro listing
        setup_logging("INFO")
        logger = logging.getLogger("MacroLister")
        
        logger.info("Connecting to Moonraker to detect G-code macros...")
        
        try:
            # Create minimal config for macro detection
            config = BridgeConfig(
                serial_port="/dev/null",  # Not needed for macro detection
                baud_rate=115200,         # Not needed for macro detection
                moonraker_host=args.moonraker_host,
                moonraker_port=args.moonraker_port,
                test_mode=True            # Safe mode
            )
            
            # Create bridge components
            moonraker = MoonrakerClient(config)
            translator = GCodeTranslator(moonraker)
            
            # Start moonraker and check macros
            await moonraker.start()
            await translator.check_available_macros()
            
            # List the macros
            translator.list_all_macros()
            
            # Clean up
            await moonraker.stop()
            
        except Exception as e:
            logger.error(f"Failed to connect to Moonraker: {e}")
            logger.error(f"Make sure Moonraker is running on {args.moonraker_host}:{args.moonraker_port}")
            return 1
        
        return 0
    
    # Check Python compatibility
    if not check_version_compatibility():
        print("Consider upgrading Python for best compatibility")
        print()
    
    # Handle standalone mode auto-detection and setup
    if args.standalone:
        # Auto-detect serial port if not provided
        if not args.serial_port:
            import glob
            # Look for common serial devices
            possible_ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
            if possible_ports:
                args.serial_port = possible_ports[0]
                print(f"🚀 Standalone mode: Auto-detected serial port {args.serial_port}")
            else:
                args.serial_port = "/dev/ttyUSB0"  # Default fallback
                print(f"🚀 Standalone mode: Using default serial port {args.serial_port}")
        
        # In standalone mode, dependencies should already be installed by the wrapper script
        try:
            import serial, aiohttp
            print("✓ Dependencies available")
        except ImportError as e:
            print(f"✗ Missing dependency: {e}")
            print("Please install dependencies first:")
            if os.path.exists("requirements.txt"):
                print("  pip3 install --user -r requirements.txt")
            else:
                print("  pip3 install --user pyserial websockets requests aiohttp")
            print("Or use the standalone wrapper: ./run_standalone.sh")
            return 1
    elif not args.serial_port:
        print("Error: --serial-port is required (or use --standalone mode)")
        return 1
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger("Main")
    
    try:
        # Create and validate configuration
        config = BridgeConfig(
            serial_port=args.serial_port,
            baud_rate=args.baud_rate,
            moonraker_host=args.moonraker_host,
            moonraker_port=args.moonraker_port,
            log_level=args.log_level,
            timeout=args.timeout,
            max_retries=args.max_retries,
            test_mode=args.test_mode,
            standalone_mode=args.standalone
        )
        
        logger.info("Configuration validated successfully")
        logger.info(f"Bridge configuration: {config}")
        
        # Create and run bridge
        bridge = TFTMoonrakerBridge(config)
        success = await bridge.run()
        
        return 0 if success else 1
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nBridge interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)