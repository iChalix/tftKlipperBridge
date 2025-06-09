#!/bin/bash

# TFT Bridge Standalone Runner
# Zero setup required - just download and run!

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    clear
    echo -e "${CYAN}"
    echo "==============================================="
    echo "   TFT Bridge - Standalone Mode"
    echo "==============================================="
    echo -e "${NC}"
    echo "🚀 Zero setup required!"
    echo "• Interactive serial port setup"
    echo "• Auto-installs dependencies"  
    echo "• No configuration files needed"
    echo "• Ready to run immediately"
    echo ""
}

detect_serial_ports() {
    # Find all potential TFT serial devices
    local ports=()
    
    # Look for USB serial devices
    for port in /dev/ttyUSB* /dev/ttyACM* /dev/serial/by-id/*; do
        if [[ -e "$port" ]]; then
            ports+=("$port")
        fi
    done
    
    # Also check for common TFT device patterns
    for port in /dev/ttyS* /dev/ttyAMA*; do
        if [[ -e "$port" && -c "$port" ]]; then
            ports+=("$port")
        fi
    done
    
    echo "${ports[@]}"
}

show_port_info() {
    local port="$1"
    echo -e "${YELLOW}Port: $port${NC}"
    
    # Try to get device info
    if command -v udevadm &> /dev/null; then
        local info=$(udevadm info --name="$port" 2>/dev/null | grep -E "(ID_VENDOR|ID_MODEL|ID_SERIAL)" | head -3)
        if [[ -n "$info" ]]; then
            echo "$info" | sed 's/^E: /  /'
        else
            echo "  No device info available"
        fi
    else
        # Fallback: check if device exists and permissions
        if [[ -c "$port" ]]; then
            local perms=$(ls -l "$port" | cut -d' ' -f1,3,4)
            echo "  Permissions: $perms"
        fi
    fi
    
    # Check if port is accessible
    if [[ -r "$port" && -w "$port" ]]; then
        echo -e "  ${GREEN}✓ Accessible${NC}"
    else
        echo -e "  ${RED}✗ Permission denied${NC}"
        echo "    Run: sudo usermod -a -G dialout $USER"
        echo "    Then log out and back in"
    fi
    echo ""
}

interactive_port_selection() {
    echo -e "${BLUE}Detecting serial ports...${NC}"
    local ports=($(detect_serial_ports))
    
    if [[ ${#ports[@]} -eq 0 ]]; then
        echo -e "${RED}No serial ports detected!${NC}"
        echo ""
        echo "Common causes:"
        echo "• TFT not connected via USB"
        echo "• USB cable is power-only (no data)"
        echo "• Device not recognized by system"
        echo ""
        read -p "Enter serial port manually (e.g., /dev/ttyUSB0): " manual_port
        if [[ -n "$manual_port" ]]; then
            echo -e "${GREEN}Selected: $manual_port${NC}"
            SERIAL_PORT="$manual_port"
        else
            echo -e "${GREEN}Selected: /dev/ttyUSB0 (default)${NC}"
            SERIAL_PORT="/dev/ttyUSB0"  # fallback
        fi
        return
    fi
    
    echo -e "${GREEN}Found ${#ports[@]} serial port(s):${NC}"
    echo ""
    
    # Show all detected ports with info
    for i in "${!ports[@]}"; do
        echo -e "${CYAN}[$((i+1))] ${ports[i]}${NC}"
        show_port_info "${ports[i]}"
    done
    
    # If only one port, ask for confirmation instead of auto-selecting
    if [[ ${#ports[@]} -eq 1 ]]; then
        echo -e "${GREEN}Found one serial port: ${ports[0]}${NC}"
        echo ""
        read -p "Use this port? (Y/n): " confirm
        if [[ -z "$confirm" || "$confirm" =~ ^[Yy]$ ]]; then
            echo ""
            echo -e "${GREEN}Selected: ${ports[0]}${NC}"
            SERIAL_PORT="${ports[0]}"
            return
        else
            echo ""
            read -p "Enter serial port manually: " manual_port
            if [[ -n "$manual_port" ]]; then
                echo ""
                echo -e "${GREEN}Selected: $manual_port${NC}"
                SERIAL_PORT="$manual_port"
            else
                echo ""
                echo -e "${GREEN}Selected: ${ports[0]}${NC}"
                SERIAL_PORT="${ports[0]}"  # fallback to detected port
            fi
            return
        fi
    fi
    
    # Let user choose
    while true; do
        echo "Select serial port:"
        for i in "${!ports[@]}"; do
            echo "  $((i+1))) ${ports[i]}"
        done
        echo "  m) Enter manually"
        echo ""
        read -p "Choice [1]: " choice
        
        # Default to first port
        if [[ -z "$choice" ]]; then
            choice=1
        fi
        
        # Handle manual entry
        if [[ "$choice" == "m" || "$choice" == "M" ]]; then
            read -p "Enter serial port: " manual_port
            if [[ -n "$manual_port" ]]; then
                echo ""
                echo -e "${GREEN}Selected: $manual_port${NC}"
                SERIAL_PORT="$manual_port"
                return
            fi
            continue
        fi
        
        # Validate numeric choice
        if [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -ge 1 ]] && [[ $choice -le ${#ports[@]} ]]; then
            selected_port="${ports[$((choice-1))]}"
            echo ""
            echo -e "${GREEN}Selected: $selected_port${NC}"
            SERIAL_PORT="$selected_port"
            return
        fi
        
        echo -e "${RED}Invalid choice. Please try again.${NC}"
        echo ""
    done
}

baud_rate_selection() {
    echo -e "${BLUE}Baud Rate Selection:${NC}"
    echo ""
    echo "Common TFT baud rates:"
    echo "  1) 250000 (most common - BigTreeTech default)"
    echo "  2) 115200 (standard serial)"
    echo "  3) 230400 (high speed)"
    echo "  4) 57600  (older devices)"
    echo "  5) Custom"
    echo ""
    echo -e "${YELLOW}Most TFT touchscreens use 250000 baud rate${NC}"
    echo ""
    
    read -p "Select baud rate [1]: " baud_choice
    
    case "${baud_choice:-1}" in
        1) BAUD_RATE="250000" ;;
        2) BAUD_RATE="115200" ;;
        3) BAUD_RATE="230400" ;;
        4) BAUD_RATE="57600" ;;
        5) 
            read -p "Enter custom baud rate: " custom_baud
            if [[ "$custom_baud" =~ ^[0-9]+$ ]]; then
                BAUD_RATE="$custom_baud"
            else
                BAUD_RATE="250000"  # fallback
            fi
            ;;
        *) BAUD_RATE="250000" ;;  # default
    esac
    
    echo ""
    echo -e "${GREEN}Selected baud rate: $BAUD_RATE${NC}"
}

print_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help"
    echo "  -t, --test              Run in test mode (safe, no printer commands)"
    echo "  -p PORT                 Specify serial port (interactive setup if omitted)"
    echo "  -b BAUD                 Specify baud rate (default: 250000)"
    echo "  -v, --verbose           Enable debug logging"
    echo "  -y, --yes               Non-interactive mode (auto-detect/use defaults)"
    echo ""
    echo "Advanced:"
    echo "  --list-macros           List all G-code macros from Klipper"
    echo ""
    echo "Examples:"
    echo "  $0                      # Interactive setup, then run"
    echo "  $0 --test              # Interactive setup, safe test mode"
    echo "  $0 -p /dev/ttyACM0      # Use specific port, skip setup"
    echo "  $0 -y                   # Auto-detect everything, no questions"
    echo "  $0 -b 115200 --verbose  # Custom baud rate with debug"
    echo "  $0 --list-macros        # Show available Klipper macros"
    echo ""
}

# Parse command line arguments
SERIAL_PORT=""
BAUD_RATE="250000"
TEST_MODE=""
LOG_LEVEL="INFO"
INTERACTIVE=true

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            print_header
            print_help
            exit 0
            ;;
        -t|--test)
            TEST_MODE="--test-mode"
            shift
            ;;
        -p)
            SERIAL_PORT="$2"
            INTERACTIVE=false
            shift 2
            ;;
        -b)
            BAUD_RATE="$2"
            shift 2
            ;;
        -v|--verbose)
            LOG_LEVEL="DEBUG"
            shift
            ;;
        -y|--yes)
            INTERACTIVE=false
            shift
            ;;
        --list-macros)
            echo -e "${CYAN}Listing G-code macros from Klipper...${NC}"
            python3 tft_moonraker_bridge.py --list-macros
            exit $?
            ;;
        *)
            echo "Unknown option: $1"
            print_help
            exit 1
            ;;
    esac
done

print_header

# Check and install dependencies FIRST
check_and_install_dependencies() {
    echo -e "${BLUE}Checking Python dependencies...${NC}"
    
    # List of required packages
    local required_packages=("serial" "aiohttp" "websockets" "requests")
    local missing_packages=()
    
    # Check each package
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            case $package in
                "serial") missing_packages+=("pyserial") ;;
                *) missing_packages+=("$package") ;;
            esac
        fi
    done
    
    if [[ ${#missing_packages[@]} -eq 0 ]]; then
        echo -e "${GREEN}✓ All dependencies are installed${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}⚠ Missing dependencies: ${missing_packages[*]}${NC}"
    echo ""
    
    # Try to install automatically
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    
    # Method 1: Try requirements.txt if available
    if [[ -f "requirements.txt" ]]; then
        echo "Using requirements.txt..."
        if pip3 install --user -r requirements.txt; then
            echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ Failed to install from requirements.txt, trying individual packages...${NC}"
        fi
    fi
    
    # Method 2: Install individual packages
    echo "Installing individual packages..."
    local install_cmd="pip3 install --user"
    for package in "${missing_packages[@]}"; do
        install_cmd+=" $package"
    done
    
    if $install_cmd; then
        echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to install dependencies automatically${NC}"
        echo ""
        echo "Please install manually:"
        if [[ -f "requirements.txt" ]]; then
            echo "  ${YELLOW}pip3 install --user -r requirements.txt${NC}"
        else
            echo "  ${YELLOW}pip3 install --user ${missing_packages[*]}${NC}"
        fi
        echo ""
        echo "Or try with system packages:"
        echo "  ${YELLOW}sudo apt install python3-serial python3-aiohttp python3-websockets python3-requests${NC}"
        echo ""
        
        if [[ "$INTERACTIVE" == "true" ]]; then
            read -p "Continue anyway (bridge will likely fail)? (y/n): " -r
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            echo "Non-interactive mode: exiting due to missing dependencies"
            exit 1
        fi
    fi
}

# Check dependencies before proceeding
check_and_install_dependencies
echo ""

# Interactive setup if no port specified
if [[ -z "$SERIAL_PORT" && "$INTERACTIVE" == "true" ]]; then
    echo -e "${CYAN}=== Serial Port Setup ===${NC}"
    echo ""
    
    # Call the interactive function directly (not captured)
    interactive_port_selection
    # The function will set SERIAL_PORT globally
    
    echo ""
    echo "Press Enter to continue to baud rate selection..."
    read -r
    
    echo -e "${CYAN}=== Baud Rate Setup ===${NC}"
    echo ""
    
    # Call the baud rate function directly (not captured)
    baud_rate_selection
    # The function will set BAUD_RATE globally
    
    echo ""
    echo "Press Enter to continue..."
    read -r
    
elif [[ -z "$SERIAL_PORT" ]]; then
    # Non-interactive mode - auto-detect
    echo -e "${BLUE}Auto-detecting serial ports...${NC}"
    local ports=($(detect_serial_ports))
    if [[ ${#ports[@]} -gt 0 ]]; then
        SERIAL_PORT="${ports[0]}"
        echo -e "${GREEN}Auto-detected serial port: $SERIAL_PORT${NC}"
    else
        SERIAL_PORT="/dev/ttyUSB0"
        echo -e "${YELLOW}No ports detected, using default: $SERIAL_PORT${NC}"
    fi
fi

# Validate serial port exists (warning only)
if [[ ! -e "$SERIAL_PORT" ]]; then
    echo -e "${YELLOW}⚠ Warning: Serial port $SERIAL_PORT does not exist${NC}"
    echo "The bridge will wait for the device to become available"
    echo ""
fi

# Check permissions
if [[ -e "$SERIAL_PORT" && ! -r "$SERIAL_PORT" ]]; then
    echo -e "${RED}✗ Permission denied: $SERIAL_PORT${NC}"
    echo "Fix with: sudo usermod -a -G dialout $USER"
    echo "Then log out and back in"
    echo ""
    if [[ "$INTERACTIVE" == "true" ]]; then
        read -p "Continue anyway? (y/n): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
fi

# Check if bridge script exists
if [[ ! -f "tft_moonraker_bridge.py" ]]; then
    echo -e "${RED}✗ Bridge script not found!${NC}"
    echo "Please download the complete tftKlipperBridge folder or run from the correct directory"
    echo ""
    echo "Quick download:"
    echo "  git clone https://github.com/bigtreetech/BIGTREETECH-TouchScreenFirmware.git"
    echo "  cd BIGTREETECH-TouchScreenFirmware/tftKlipperBridge"
    echo "  ./run_standalone.sh"
    exit 1
fi

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found!${NC}"
    echo "Please install Python 3 first:"
    echo "  sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Show configuration
echo -e "${BLUE}Configuration Summary:${NC}"
echo "  Serial Port: $SERIAL_PORT"
echo "  Baud Rate:   $BAUD_RATE"
echo "  Moonraker:   localhost:7125 (default)"
echo "  Log Level:   $LOG_LEVEL"
if [[ -n "$TEST_MODE" ]]; then
    echo "  Mode:        🧪 TEST MODE (safe)"
else
    echo "  Mode:        🚀 PRODUCTION MODE"
fi
echo ""

if [[ -n "$TEST_MODE" ]]; then
    echo -e "${YELLOW}🧪 TEST MODE ENABLED${NC}"
    echo "• Commands will be logged but NOT executed"
    echo "• Safe to test TFT communication"
    echo "• No risk to your printer"
else
    echo -e "${YELLOW}⚠ PRODUCTION MODE${NC}"
    echo "• Commands WILL be sent to your printer"
    echo "• Make sure Klipper/Moonraker are running"
    echo "• Use --test flag first to verify setup"
    echo ""
    echo -e "${CYAN}Moonraker Connection Tips:${NC}"
    echo "• Default: localhost:7125 (same machine as bridge)"
    echo "• Remote: Use --moonraker-host IP_ADDRESS"
    echo "• Check: curl http://localhost:7125/printer/info"
fi

echo ""

# Ask for final confirmation in interactive mode
if [[ "$INTERACTIVE" == "true" ]]; then
    echo -e "${CYAN}Ready to start TFT Bridge with above configuration.${NC}"
    echo ""
    read -p "Start the bridge now? (Y/n): " start_confirm
    if [[ -n "$start_confirm" && ! "$start_confirm" =~ ^[Yy]$ ]]; then
        echo "Bridge startup cancelled."
        exit 0
    fi
    echo ""
fi

echo -e "${CYAN}Starting TFT Bridge...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Build command
CMD="python3 tft_moonraker_bridge.py --standalone --serial-port $SERIAL_PORT --baud-rate $BAUD_RATE --log-level $LOG_LEVEL $TEST_MODE"

# Run the bridge
exec $CMD