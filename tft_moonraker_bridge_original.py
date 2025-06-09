#!/usr/bin/env python3
"""
TFT Moonraker Bridge - Translates TFT G-codes to Moonraker API calls

This script acts as a bridge between BigTreeTech TFT touchscreens and Klipper via Moonraker.
It intercepts G-codes sent by the TFT and translates them to appropriate Moonraker API calls.

Author: Claude Code
License: GPL-3.0
"""

import serial
import asyncio
import websockets
import json
import re
import argparse
import logging
import sys
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import requests
from urllib.parse import urljoin


@dataclass
class BridgeConfig:
    """Configuration for the TFT-Moonraker bridge"""
    serial_port: str
    baud_rate: int
    moonraker_host: str = "localhost"
    moonraker_port: int = 7125
    log_level: str = "INFO"
    timeout: float = 5.0


class MoonrakerClient:
    """Handles communication with Moonraker API"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.base_url = f"http://{config.moonraker_host}:{config.moonraker_port}"
        self.websocket = None
        self.logger = logging.getLogger("MoonrakerClient")
        
    async def connect_websocket(self):
        """Connect to Moonraker websocket for real-time updates"""
        try:
            ws_url = f"ws://{self.config.moonraker_host}:{self.config.moonraker_port}/websocket"
            self.websocket = await websockets.connect(ws_url)
            self.logger.info("Connected to Moonraker websocket")
        except Exception as e:
            self.logger.error(f"Failed to connect to websocket: {e}")
            
    async def send_gcode(self, gcode: str) -> Dict[str, Any]:
        """Send G-code to Klipper via Moonraker"""
        try:
            url = urljoin(self.base_url, "/printer/gcode/script")
            data = {"script": gcode}
            response = requests.post(url, json=data, timeout=self.config.timeout)
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to send G-code '{gcode}': {e}")
            return {"error": str(e)}
            
    async def get_printer_status(self) -> Dict[str, Any]:
        """Get current printer status"""
        try:
            url = urljoin(self.base_url, "/printer/objects/query?extruder&heater_bed&fan&toolhead&print_stats")
            response = requests.get(url, timeout=self.config.timeout)
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get printer status: {e}")
            return {"error": str(e)}
            
    async def start_print(self, filename: str) -> Dict[str, Any]:
        """Start a print job"""
        try:
            url = urljoin(self.base_url, "/printer/print/start")
            data = {"filename": filename}
            response = requests.post(url, json=data, timeout=self.config.timeout)
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to start print: {e}")
            return {"error": str(e)}
            
    async def pause_print(self) -> Dict[str, Any]:
        """Pause current print"""
        try:
            url = urljoin(self.base_url, "/printer/print/pause")
            response = requests.post(url, timeout=self.config.timeout)
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to pause print: {e}")
            return {"error": str(e)}
            
    async def resume_print(self) -> Dict[str, Any]:
        """Resume paused print"""
        try:
            url = urljoin(self.base_url, "/printer/print/resume")
            response = requests.post(url, timeout=self.config.timeout)
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to resume print: {e}")
            return {"error": str(e)}
            
    async def cancel_print(self) -> Dict[str, Any]:
        """Cancel current print"""
        try:
            url = urljoin(self.base_url, "/printer/print/cancel")
            response = requests.post(url, timeout=self.config.timeout)
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to cancel print: {e}")
            return {"error": str(e)}


class GCodeTranslator:
    """Translates TFT G-codes to Moonraker API calls or Klipper macros"""
    
    def __init__(self, moonraker_client: MoonrakerClient):
        self.moonraker = moonraker_client
        self.logger = logging.getLogger("GCodeTranslator")
        self.available_macros = set()
        self.macros_checked = False
        
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
        """Check what macros are available in Klipper"""
        if self.macros_checked:
            return
            
        try:
            url = urljoin(self.moonraker.base_url, "/printer/objects/query?configfile")
            response = requests.get(url, timeout=self.moonraker.config.timeout)
            data = response.json()
            
            if "result" in data and "status" in data["result"] and "configfile" in data["result"]["status"]:
                config = data["result"]["status"]["configfile"]["settings"]
                
                # Find all gcode_macro entries
                for key in config.keys():
                    if key.startswith("gcode_macro "):
                        macro_name = key.replace("gcode_macro ", "").upper()
                        self.available_macros.add(macro_name)
                        
                self.logger.info(f"Found {len(self.available_macros)} available macros")
                self.logger.debug(f"Available macros: {sorted(self.available_macros)}")
                
        except Exception as e:
            self.logger.warning(f"Could not check available macros: {e}")
        finally:
            self.macros_checked = True
    
    async def translate_gcode(self, gcode: str) -> Optional[str]:
        """Translate a G-code command to Klipper equivalent"""
        gcode = gcode.strip()
        
        # Check available macros if we haven't already
        await self.check_available_macros()
        
        # Special handling for filament commands if user has existing macros
        if gcode.upper() == "M701":
            if "LOAD_FILAMENT" in self.available_macros:
                self.logger.info("Using existing LOAD_FILAMENT macro")
                return "LOAD_FILAMENT"
            else:
                self.logger.warning("No LOAD_FILAMENT macro found, using fallback")
                return "TFT_LOAD_FILAMENT"
                
        if gcode.upper() == "M702":
            if "UNLOAD_FILAMENT" in self.available_macros:
                self.logger.info("Using existing UNLOAD_FILAMENT macro")
                return "UNLOAD_FILAMENT"
            else:
                self.logger.warning("No UNLOAD_FILAMENT macro found, using fallback")
                return "TFT_UNLOAD_FILAMENT"
        
        # Check for direct translations
        for pattern, replacement in self.translations.items():
            match = re.match(pattern, gcode, re.IGNORECASE)
            if match:
                if callable(replacement):
                    return replacement(match)
                else:
                    return replacement
                    
        # Pass through standard G-codes that work in Klipper
        passthrough_patterns = [
            r"G[01]\s+.*",  # Movement commands
            r"G28.*",       # Homing
            r"G9[01]",      # Positioning modes
            r"G92.*",       # Set position
            r"M10[4-9].*",  # Temperature commands
            r"M1[14-15].*", # Misc commands
            r"M1[89]0.*",   # Bed temperature
            r"M220.*",      # Speed factor
            r"M221.*",      # Flow factor
            r"M[23][0-9].*" # Print control
        ]
        
        for pattern in passthrough_patterns:
            if re.match(pattern, gcode, re.IGNORECASE):
                return gcode
                
        # Commands that need special handling
        if gcode.upper().startswith("M115"):
            return None  # Will be handled specially
        elif gcode.upper().startswith("M105"):
            return None  # Temperature reporting handled specially
            
        self.logger.warning(f"No translation found for: {gcode}")
        return None


class TFTSerial:
    """Handles serial communication with TFT"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.serial = None
        self.logger = logging.getLogger("TFTSerial")
        
    def connect(self):
        """Connect to TFT serial port"""
        try:
            self.serial = serial.Serial(
                port=self.config.serial_port,
                baudrate=self.config.baud_rate,
                timeout=1.0,
                write_timeout=1.0
            )
            self.logger.info(f"Connected to TFT on {self.config.serial_port} at {self.config.baud_rate} baud")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to TFT: {e}")
            return False
            
    def read_line(self) -> Optional[str]:
        """Read a line from TFT"""
        try:
            if self.serial and self.serial.in_waiting:
                line = self.serial.readline().decode('utf-8').strip()
                return line
        except Exception as e:
            self.logger.error(f"Error reading from TFT: {e}")
        return None
        
    def write_line(self, data: str):
        """Write a line to TFT"""
        try:
            if self.serial:
                self.serial.write(f"{data}\n".encode('utf-8'))
                self.serial.flush()
        except Exception as e:
            self.logger.error(f"Error writing to TFT: {e}")
            
    def close(self):
        """Close serial connection"""
        if self.serial:
            self.serial.close()


class TFTMoonrakerBridge:
    """Main bridge class that coordinates between TFT and Moonraker"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.logger = logging.getLogger("TFTBridge")
        
        self.tft = TFTSerial(config)
        self.moonraker = MoonrakerClient(config)
        self.translator = GCodeTranslator(self.moonraker)
        
        self.running = False
        self.last_temp_report = 0
        self.temp_report_interval = 2.0  # seconds
        
    async def handle_m115(self):
        """Handle M115 firmware info request"""
        # Send Marlin-like response to make TFT happy
        response = "FIRMWARE_NAME:Klipper FIRMWARE_VERSION:v0.11.0 PROTOCOL_VERSION:1.0"
        self.tft.write_line(response)
        self.tft.write_line("ok")
        
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
                    
                response = "ok " + " ".join(temp_parts)
                self.tft.write_line(response)
            else:
                self.tft.write_line("ok T:0.0 /0.0 B:0.0 /0.0")
        except Exception as e:
            self.logger.error(f"Error handling M105: {e}")
            self.tft.write_line("ok T:0.0 /0.0 B:0.0 /0.0")
            
    async def send_periodic_updates(self):
        """Send periodic temperature updates to TFT"""
        while self.running:
            current_time = time.time()
            if current_time - self.last_temp_report >= self.temp_report_interval:
                await self.handle_m105()
                self.last_temp_report = current_time
            await asyncio.sleep(0.5)
            
    async def process_gcode(self, gcode: str):
        """Process a G-code from TFT"""
        gcode = gcode.strip()
        if not gcode:
            return
            
        self.logger.debug(f"Received: {gcode}")
        
        # Handle special commands
        if gcode.upper().startswith("M115"):
            await self.handle_m115()
            return
        elif gcode.upper().startswith("M105"):
            await self.handle_m105()
            return
            
        # Translate G-code
        translated = await self.translator.translate_gcode(gcode)
        
        if translated:
            self.logger.info(f"Translating '{gcode}' -> '{translated}'")
            result = await self.moonraker.send_gcode(translated)
            
            if "error" in result:
                self.tft.write_line(f"!! {result['error']}")
            else:
                self.tft.write_line("ok")
        else:
            # Unknown command, send ok to keep TFT happy
            self.logger.warning(f"Unknown command: {gcode}")
            self.tft.write_line("ok")
            
    async def run(self):
        """Main bridge loop"""
        self.logger.info("Starting TFT-Moonraker bridge...")
        
        # Connect to TFT
        if not self.tft.connect():
            self.logger.error("Failed to connect to TFT")
            return False
            
        # Connect to Moonraker websocket
        await self.moonraker.connect_websocket()
        
        self.running = True
        
        # Start periodic updates
        update_task = asyncio.create_task(self.send_periodic_updates())
        
        try:
            while self.running:
                # Read from TFT
                line = self.tft.read_line()
                if line:
                    await self.process_gcode(line)
                    
                await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down bridge...")
        except Exception as e:
            self.logger.error(f"Bridge error: {e}")
        finally:
            self.running = False
            update_task.cancel()
            self.tft.close()
            
        return True


def setup_logging(level: str):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('tft_bridge.log')
        ]
    )


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="TFT-Moonraker Bridge")
    parser.add_argument("--serial-port", "-p", required=True, 
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
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Create configuration
    config = BridgeConfig(
        serial_port=args.serial_port,
        baud_rate=args.baud_rate,
        moonraker_host=args.moonraker_host,
        moonraker_port=args.moonraker_port,
        log_level=args.log_level,
        timeout=args.timeout
    )
    
    # Create and run bridge
    bridge = TFTMoonrakerBridge(config)
    await bridge.run()


if __name__ == "__main__":
    asyncio.run(main())