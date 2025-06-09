#!/bin/bash

# TFT-Moonraker Bridge Setup Script
# This script helps configure and install the TFT bridge service

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables - EDIT THESE TO MATCH YOUR SETUP
#################################################################

# TFT Serial Configuration
TFT_SERIAL_PORT="/dev/ttyUSB0"          # Serial port for TFT connection
TFT_BAUD_RATE="250000"                  # Baud rate (115200, 250000, etc.)

# Moonraker Configuration  
MOONRAKER_HOST="localhost"              # Moonraker host IP/hostname
MOONRAKER_PORT="7125"                   # Moonraker port

# Bridge Configuration
BRIDGE_LOG_LEVEL="INFO"                 # Log level: DEBUG, INFO, WARNING, ERROR
BRIDGE_TIMEOUT="5.0"                    # Request timeout in seconds
BRIDGE_USER="pi"                        # User to run the service as
BRIDGE_INSTALL_DIR="/home/${BRIDGE_USER}" # Installation directory

# Service Configuration
SERVICE_NAME="tft-bridge"               # Systemd service name
AUTO_START="yes"                        # Auto-start service on boot (yes/no)

# Klipper Configuration
KLIPPER_CONFIG_DIR="/home/${BRIDGE_USER}/printer_data/config"  # Klipper config directory
KLIPPER_CONFIG_FILE="printer.cfg"      # Main Klipper config file

#################################################################

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "======================================"
    echo "  TFT-Moonraker Bridge Setup Script"
    echo "======================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root!"
        exit 1
    fi
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed!"
        exit 1
    fi
    print_success "Python 3 found"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed!"
        exit 1
    fi
    print_success "pip3 found"
    
    # Check serial port exists
    if [[ ! -e "$TFT_SERIAL_PORT" ]]; then
        print_warning "Serial port $TFT_SERIAL_PORT does not exist yet"
        print_info "This is normal if TFT is not connected. Please connect before starting the service."
    else
        print_success "Serial port $TFT_SERIAL_PORT found"
    fi
    
    # Check if user is in dialout group
    if ! groups $USER | grep -q dialout; then
        print_warning "User $USER is not in 'dialout' group"
        print_info "Adding user to dialout group..."
        sudo usermod -a -G dialout $USER
        print_success "User added to dialout group"
        print_warning "You may need to log out and back in for group changes to take effect"
    else
        print_success "User is in dialout group"
    fi
}

install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Try to use requirements.txt if available, otherwise fallback to individual packages
    if [[ -f "requirements.txt" ]]; then
        pip3 install --user -r requirements.txt || {
            print_warning "Failed to install from requirements.txt, trying individual packages..."
            pip3 install --user pyserial websockets requests aiohttp || {
                print_error "Failed to install Python dependencies"
                exit 1
            }
        }
    else
        pip3 install --user pyserial websockets requests aiohttp || {
            print_error "Failed to install Python dependencies"
            exit 1
        }
    fi
    
    print_success "Python dependencies installed"
}

display_configuration() {
    print_info "Current configuration:"
    echo "  TFT Serial Port:    $TFT_SERIAL_PORT"
    echo "  TFT Baud Rate:      $TFT_BAUD_RATE"
    echo "  Moonraker Host:     $MOONRAKER_HOST"
    echo "  Moonraker Port:     $MOONRAKER_PORT"
    echo "  Log Level:          $BRIDGE_LOG_LEVEL"
    echo "  Install Directory:  $BRIDGE_INSTALL_DIR"
    echo "  Service User:       $BRIDGE_USER"
    echo "  Auto Start:         $AUTO_START"
    echo ""
    
    read -p "Continue with this configuration? (y/n): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Edit the variables at the top of this script and run again"
        exit 0
    fi
}

copy_bridge_files() {
    print_info "Copying bridge files..."
    
    # Copy main bridge script
    cp tft_moonraker_bridge.py "$BRIDGE_INSTALL_DIR/" || {
        print_error "Failed to copy bridge script"
        exit 1
    }
    chmod +x "$BRIDGE_INSTALL_DIR/tft_moonraker_bridge.py"
    print_success "Bridge script copied"
    
    # Copy Klipper macros
    if [[ -d "$KLIPPER_CONFIG_DIR" ]]; then
        cp klipper_tft_macros.cfg "$KLIPPER_CONFIG_DIR/" || {
            print_error "Failed to copy Klipper macros"
            exit 1
        }
        print_success "Klipper macros copied to $KLIPPER_CONFIG_DIR"
        
        # Check if macros are included in printer.cfg
        if ! grep -q "klipper_tft_macros.cfg" "$KLIPPER_CONFIG_DIR/$KLIPPER_CONFIG_FILE" 2>/dev/null; then
            print_warning "Klipper macros not included in $KLIPPER_CONFIG_FILE"
            print_info "Adding include statement..."
            echo "" >> "$KLIPPER_CONFIG_DIR/$KLIPPER_CONFIG_FILE"
            echo "# TFT Bridge Macros" >> "$KLIPPER_CONFIG_DIR/$KLIPPER_CONFIG_FILE"
            echo "[include klipper_tft_macros.cfg]" >> "$KLIPPER_CONFIG_DIR/$KLIPPER_CONFIG_FILE"
            print_success "Include statement added to $KLIPPER_CONFIG_FILE"
        else
            print_success "Macros already included in $KLIPPER_CONFIG_FILE"
        fi
    else
        print_warning "Klipper config directory not found at $KLIPPER_CONFIG_DIR"
        print_info "Please manually copy klipper_tft_macros.cfg to your Klipper config directory"
    fi
}

create_systemd_service() {
    print_info "Creating systemd service..."
    
    # Create service file
    sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=TFT Moonraker Bridge
After=network.target klipper.service moonraker.service
Wants=klipper.service moonraker.service

[Service]
Type=simple
User=${BRIDGE_USER}
Group=${BRIDGE_USER}
WorkingDirectory=${BRIDGE_INSTALL_DIR}
ExecStart=/usr/bin/python3 ${BRIDGE_INSTALL_DIR}/tft_moonraker_bridge.py \\
    --serial-port ${TFT_SERIAL_PORT} \\
    --baud-rate ${TFT_BAUD_RATE} \\
    --moonraker-host ${MOONRAKER_HOST} \\
    --moonraker-port ${MOONRAKER_PORT} \\
    --log-level ${BRIDGE_LOG_LEVEL} \\
    --timeout ${BRIDGE_TIMEOUT}

Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    print_success "Systemd service created"
    
    # Reload systemd
    sudo systemctl daemon-reload
    print_success "Systemd daemon reloaded"
    
    # Enable service if auto-start is enabled
    if [[ "$AUTO_START" == "yes" ]]; then
        sudo systemctl enable ${SERVICE_NAME}.service
        print_success "Service enabled for auto-start"
    fi
}

create_start_script() {
    print_info "Creating start script..."
    
    # Create a convenient start script
    tee "$BRIDGE_INSTALL_DIR/start_tft_bridge.sh" > /dev/null << EOF
#!/bin/bash
# TFT Bridge Start Script
# Generated by setup script

cd "$BRIDGE_INSTALL_DIR"

python3 tft_moonraker_bridge.py \\
    --serial-port $TFT_SERIAL_PORT \\
    --baud-rate $TFT_BAUD_RATE \\
    --moonraker-host $MOONRAKER_HOST \\
    --moonraker-port $MOONRAKER_PORT \\
    --log-level $BRIDGE_LOG_LEVEL \\
    --timeout $BRIDGE_TIMEOUT
EOF

    chmod +x "$BRIDGE_INSTALL_DIR/start_tft_bridge.sh"
    print_success "Start script created at $BRIDGE_INSTALL_DIR/start_tft_bridge.sh"
}

create_config_file() {
    print_info "Creating configuration file..."
    
    # Create a config file for easy editing
    tee "$BRIDGE_INSTALL_DIR/tft_bridge.conf" > /dev/null << EOF
# TFT Bridge Configuration
# Edit these values and restart the service

TFT_SERIAL_PORT=$TFT_SERIAL_PORT
TFT_BAUD_RATE=$TFT_BAUD_RATE
MOONRAKER_HOST=$MOONRAKER_HOST
MOONRAKER_PORT=$MOONRAKER_PORT
BRIDGE_LOG_LEVEL=$BRIDGE_LOG_LEVEL
BRIDGE_TIMEOUT=$BRIDGE_TIMEOUT
EOF

    print_success "Configuration file created at $BRIDGE_INSTALL_DIR/tft_bridge.conf"
}

check_services() {
    print_info "Checking related services..."
    
    # Check Klipper
    if systemctl is-active --quiet klipper; then
        print_success "Klipper service is running"
    else
        print_warning "Klipper service is not running"
    fi
    
    # Check Moonraker  
    if systemctl is-active --quiet moonraker; then
        print_success "Moonraker service is running"
    else
        print_warning "Moonraker service is not running"
    fi
    
    # Test Moonraker API
    if curl -s "http://${MOONRAKER_HOST}:${MOONRAKER_PORT}/printer/info" &>/dev/null; then
        print_success "Moonraker API is accessible"
    else
        print_warning "Moonraker API is not accessible at http://${MOONRAKER_HOST}:${MOONRAKER_PORT}"
    fi
}

print_final_instructions() {
    print_info "Installation complete!"
    echo ""
    echo "Next steps:"
    echo "1. Restart Klipper to load the new macros:"
    echo "   sudo systemctl restart klipper"
    echo ""
    echo "2. Start the TFT bridge service:"
    echo "   sudo systemctl start ${SERVICE_NAME}"
    echo ""
    echo "3. Check service status:"
    echo "   sudo systemctl status ${SERVICE_NAME}"
    echo ""
    echo "4. View logs:"
    echo "   sudo journalctl -u ${SERVICE_NAME} -f"
    echo ""
    echo "5. Manual start (for testing):"
    echo "   $BRIDGE_INSTALL_DIR/start_tft_bridge.sh"
    echo ""
    echo "Configuration files:"
    echo "- Service: /etc/systemd/system/${SERVICE_NAME}.service"
    echo "- Config: $BRIDGE_INSTALL_DIR/tft_bridge.conf"
    echo "- Macros: $KLIPPER_CONFIG_DIR/klipper_tft_macros.cfg"
    echo ""
    print_success "Setup complete! Connect your TFT and start the service."
}

# Main execution
main() {
    print_header
    
    display_configuration
    check_prerequisites
    install_dependencies
    copy_bridge_files
    create_systemd_service
    create_start_script
    create_config_file
    check_services
    
    print_final_instructions
}

# Check if required files exist
if [[ ! -f "tft_moonraker_bridge.py" ]]; then
    print_error "tft_moonraker_bridge.py not found in current directory!"
    print_info "Please run this script from the tftKlipperBridge directory"
    print_info "If you're in the main repository directory, run:"
    echo "  cd tftKlipperBridge"
    echo "  ./setup_tft_bridge.sh"
    exit 1
fi

if [[ ! -f "klipper_tft_macros.cfg" ]]; then
    print_error "klipper_tft_macros.cfg not found in current directory!"
    print_info "Please run this script from the tftKlipperBridge directory"
    exit 1
fi

# Run main function
main "$@"