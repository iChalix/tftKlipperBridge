#!/bin/bash

# TFT Bridge Quick Start - Download and Run
# Ultimate convenience: one command to get started

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "=============================================="
echo "   TFT Bridge - Quick Start"
echo "=============================================="
echo -e "${NC}"
echo "🚀 One-command setup for TFT35 V2 + Klipper"
echo ""

# Check if we're already in the right directory
if [[ -f "tft_moonraker_bridge.py" ]]; then
    echo -e "${GREEN}✓ Bridge files found${NC}"
    echo "Running in standalone mode..."
    echo ""
    exec ./run_standalone.sh "$@"
fi

# Check for git
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git not found!${NC}"
    echo "Please install git first:"
    echo "  sudo apt update && sudo apt install git"
    exit 1
fi

echo -e "${BLUE}Downloading TFT Bridge...${NC}"

# Create temp directory
TEMP_DIR="/tmp/tft_bridge_$$"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Clone the repository
echo "Cloning repository..."
git clone --depth 1 https://github.com/bigtreetech/BIGTREETECH-TouchScreenFirmware.git

# Navigate to bridge directory
cd BIGTREETECH-TouchScreenFirmware/tftKlipperBridge

echo -e "${GREEN}✓ Download complete${NC}"
echo ""

# Make scripts executable
chmod +x *.sh

# Run standalone mode with arguments
echo -e "${CYAN}Starting TFT Bridge in standalone mode...${NC}"
echo ""
exec ./run_standalone.sh "$@"