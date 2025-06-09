#!/bin/bash

# TFT Bridge Test Script
# This script runs the bridge in test mode for safe testing

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "=================================="
    echo "   TFT Bridge Test Mode"
    echo "=================================="
    echo -e "${NC}"
    echo "This will run the bridge in test mode where:"
    echo "• Commands are logged but NOT executed"
    echo "• Safe to test TFT communication"
    echo "• No risk to your printer"
    echo ""
}

print_usage() {
    echo "Usage: $0 [serial_port] [baud_rate]"
    echo ""
    echo "Examples:"
    echo "  $0                           # Use defaults (/dev/ttyUSB0, 250000)"
    echo "  $0 /dev/ttyACM0              # Custom serial port"
    echo "  $0 /dev/ttyUSB0 115200       # Custom port and baud rate"
    echo ""
    echo "Available serial ports:"
    ls /dev/tty* 2>/dev/null | grep -E "(USB|ACM)" | head -5 || echo "  No USB/ACM ports found"
    echo ""
}

# Parse arguments
SERIAL_PORT="${1:-/dev/ttyUSB0}"
BAUD_RATE="${2:-250000}"

# Check if help requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    print_header
    print_usage
    exit 0
fi

print_header

# Check dependencies first
echo -e "${BLUE}Checking dependencies...${NC}"
if python3 check_dependencies.py >/dev/null 2>&1; then
    echo -e "${GREEN}✓ All dependencies available${NC}"
else
    echo -e "${YELLOW}⚠ Some dependencies missing${NC}"
    echo "Installing dependencies..."
    
    # Try to install missing dependencies
    if [[ -f "requirements.txt" ]]; then
        pip3 install --user -r requirements.txt || {
            echo -e "${RED}✗ Failed to install dependencies${NC}"
            echo "Please install manually: pip3 install --user -r requirements.txt"
            exit 1
        }
    else
        pip3 install --user pyserial aiohttp websockets requests || {
            echo -e "${RED}✗ Failed to install dependencies${NC}"
            echo "Please install manually: pip3 install --user pyserial aiohttp websockets requests"
            exit 1
        }
    fi
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi
echo ""

# Check if serial port exists
if [[ ! -e "$SERIAL_PORT" ]]; then
    echo -e "${YELLOW}⚠ Warning: Serial port $SERIAL_PORT does not exist${NC}"
    echo "Available ports:"
    ls /dev/tty* 2>/dev/null | grep -E "(USB|ACM)" | head -5 || echo "  No USB/ACM ports found"
    echo ""
    read -p "Continue anyway? (y/n): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Check if bridge script exists
if [[ ! -f "tft_moonraker_bridge.py" ]]; then
    echo -e "${RED}✗ Bridge script not found!${NC}"
    echo "Please run this script from the tftKlipperBridge directory"
    exit 1
fi

echo -e "${GREEN}Starting TFT Bridge in test mode...${NC}"
echo "Configuration:"
echo "  Serial Port: $SERIAL_PORT"
echo "  Baud Rate:   $BAUD_RATE"
echo "  Mode:        🧪 TEST MODE (safe)"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Run the bridge in test mode
python3 tft_moonraker_bridge.py \
    --serial-port "$SERIAL_PORT" \
    --baud-rate "$BAUD_RATE" \
    --log-level DEBUG \
    --test-mode