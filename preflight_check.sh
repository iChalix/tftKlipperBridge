#!/bin/bash

# TFT Bridge Pre-flight Check
# Verifies system readiness before running the bridge

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}TFT Bridge Pre-flight Check${NC}"
echo "=========================="
echo ""

EXIT_CODE=0

# 1. Check Python version
echo -n "Python 3.7+ ... "
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    EXIT_CODE=1
else
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)"; then
        echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}✗ Python $PYTHON_VERSION (need 3.7+)${NC}"
        EXIT_CODE=1
    fi
fi

# 2. Check pip3
echo -n "pip3 ... "
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓ Available${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    EXIT_CODE=1
fi

# 3. Check dependencies
echo -n "Dependencies ... "
if [[ -f "check_dependencies.py" ]]; then
    if python3 check_dependencies.py >/dev/null 2>&1; then
        echo -e "${GREEN}✓ All installed${NC}"
    else
        echo -e "${YELLOW}⚠ Some missing${NC}"
        if [[ -f "requirements.txt" ]]; then
            echo "  Install with: pip3 install --user -r requirements.txt"
        else
            echo "  Install with: pip3 install --user pyserial aiohttp websockets requests"
        fi
    fi
else
    echo -e "${YELLOW}⚠ Checker not found${NC}"
fi

# 4. Check bridge script
echo -n "Bridge script ... "
if [[ -f "tft_moonraker_bridge.py" ]]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ tft_moonraker_bridge.py not found${NC}"
    EXIT_CODE=1
fi

# 5. Check serial ports
echo -n "Serial ports ... "
PORTS=($(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null))
if [[ ${#PORTS[@]} -gt 0 ]]; then
    echo -e "${GREEN}✓ ${#PORTS[@]} found${NC}"
    for port in "${PORTS[@]}"; do
        if [[ -r "$port" && -w "$port" ]]; then
            echo "  ${port} - accessible"
        else
            echo "  ${port} - permission denied"
        fi
    done
else
    echo -e "${YELLOW}⚠ None detected${NC}"
    echo "  Connect TFT via USB or check cable"
fi

# 6. Check user groups
echo -n "dialout group ... "
if groups | grep -q dialout; then
    echo -e "${GREEN}✓ User in dialout group${NC}"
else
    echo -e "${YELLOW}⚠ User not in dialout group${NC}"
    echo "  Fix with: sudo usermod -a -G dialout $USER"
    echo "  Then log out and back in"
fi

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}🎉 Pre-flight check passed! Ready to run TFT Bridge.${NC}"
    echo ""
    echo "Quick start options:"
    echo "  ./run_standalone.sh          # Interactive setup"
    echo "  ./test_bridge.sh             # Safe test mode"
    echo "  ./install_tft_bridge.sh      # Full installation"
else
    echo -e "${RED}⚠ Pre-flight check failed. Please address the issues above.${NC}"
fi

exit $EXIT_CODE