#!/bin/bash

# TFT-Moonraker Bridge Uninstall Script
# This script completely removes the TFT bridge service and related files

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default configuration
BRIDGE_USER="${BRIDGE_USER:-pi}"
SERVICE_NAME="tft-bridge"
BRIDGE_BASE_DIR="/home/${BRIDGE_USER}"
BRIDGE_INSTALL_DIR="/home/${BRIDGE_USER}/tft-klipper-bridge"
KLIPPER_CONFIG_DIR="/home/${BRIDGE_USER}/printer_data/config"

# Functions
print_header() {
    clear
    echo -e "${CYAN}"
    echo "=============================================="
    echo "   TFT-Moonraker Bridge Uninstall Script"
    echo "=============================================="
    echo -e "${NC}"
    echo "This script will completely remove the TFT bridge"
    echo "service and all related files from your system."
    echo ""
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

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

confirm_removal() {
    echo -e "${YELLOW}WARNING: This will permanently remove:${NC}"
    echo "  • TFT bridge systemd service"
    echo "  • Service configuration files"
    echo "  • Helper scripts"
    echo "  • Log files"
    echo ""
    echo -e "${BLUE}Optional removals (you will be asked):${NC}"
    echo "  • Bridge Python script"
    echo "  • Klipper macro files"
    echo "  • Configuration files"
    echo ""
    
    read -p "Are you sure you want to proceed? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Uninstall cancelled."
        exit 0
    fi
    echo ""
}

stop_and_disable_service() {
    print_step "Stopping and disabling TFT bridge service..."
    
    # Check if service exists
    if systemctl list-unit-files | grep -q "^${SERVICE_NAME}\.service"; then
        # Stop the service
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            sudo systemctl stop "$SERVICE_NAME"
            print_success "Service stopped"
        else
            print_info "Service was not running"
        fi
        
        # Disable the service
        if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
            sudo systemctl disable "$SERVICE_NAME"
            print_success "Service disabled"
        else
            print_info "Service was not enabled"
        fi
    else
        print_info "Service not found - may already be removed"
    fi
}

remove_service_file() {
    print_step "Removing systemd service file..."
    
    local service_file="/etc/systemd/system/${SERVICE_NAME}.service"
    if [[ -f "$service_file" ]]; then
        sudo rm -f "$service_file"
        print_success "Service file removed: $service_file"
    else
        print_info "Service file not found"
    fi
    
    # Reload systemd
    sudo systemctl daemon-reload
    sudo systemctl reset-failed 2>/dev/null || true
    print_success "Systemd configuration reloaded"
}

remove_helper_scripts() {
    print_step "Removing helper scripts..."
    
    local scripts=(
        "bridge_control.sh"
        "bridge_status.sh"
        "start_bridge.sh"
        "tft_bridge_config.sh"
    )
    
    local removed_count=0
    for script in "${scripts[@]}"; do
        # Check both old location (home directory) and new location (subfolder)
        local old_path="${BRIDGE_BASE_DIR}/${script}"
        local new_path="${BRIDGE_INSTALL_DIR}/${script}"
        
        if [[ -f "$old_path" ]]; then
            rm -f "$old_path"
            print_success "Removed: $script (from home directory)"
            ((removed_count++))
        fi
        
        if [[ -f "$new_path" ]]; then
            rm -f "$new_path"
            print_success "Removed: $script (from installation directory)"
            ((removed_count++))
        fi
    done
    
    if [[ $removed_count -eq 0 ]]; then
        print_info "No helper scripts found"
    else
        print_success "Removed $removed_count helper scripts"
    fi
}

remove_log_files() {
    print_step "Removing log files..."
    
    local log_locations=(
        "${BRIDGE_BASE_DIR}"
        "${BRIDGE_INSTALL_DIR}"
    )
    
    local removed_count=0
    for location in "${log_locations[@]}"; do
        for i in {0..5}; do
            local log_file="${location}/tft_bridge.log"
            [[ $i -gt 0 ]] && log_file="${location}/tft_bridge.log.$i"
            
            if [[ -f "$log_file" ]]; then
                rm -f "$log_file"
                ((removed_count++))
            fi
        done
    done
    
    if [[ $removed_count -eq 0 ]]; then
        print_info "No log files found"
    else
        print_success "Removed $removed_count log files"
    fi
}

optional_remove_bridge_script() {
    print_step "Bridge Python script removal..."
    
    local scripts_found=false
    local scripts_to_check=(
        "${BRIDGE_BASE_DIR}/tft_moonraker_bridge.py"
        "${BRIDGE_BASE_DIR}/tft_moonraker_bridge_original.py"
        "${BRIDGE_INSTALL_DIR}/tft_moonraker_bridge.py"
        "${BRIDGE_INSTALL_DIR}/tft_moonraker_bridge_original.py"
    )
    
    # Check if any scripts exist
    for script in "${scripts_to_check[@]}"; do
        [[ -f "$script" ]] && scripts_found=true
    done
    
    if [[ "$scripts_found" == "true" ]]; then
        echo ""
        read -p "Remove bridge Python scripts? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for script in "${scripts_to_check[@]}"; do
                if [[ -f "$script" ]]; then
                    rm -f "$script"
                    print_success "Removed: $(basename "$script") (from $(dirname "$script"))"
                fi
            done
        else
            print_info "Bridge scripts preserved"
        fi
    else
        print_info "No bridge scripts found"
    fi
}

optional_remove_klipper_macros() {
    print_step "Klipper macro file removal..."
    
    local macro_file="${KLIPPER_CONFIG_DIR}/klipper_tft_macros.cfg"
    local printer_cfg="${KLIPPER_CONFIG_DIR}/printer.cfg"
    
    if [[ -f "$macro_file" ]]; then
        echo ""
        read -p "Remove Klipper TFT macro file? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f "$macro_file"
            print_success "Removed: klipper_tft_macros.cfg"
            
            # Check if include line exists in printer.cfg
            if [[ -f "$printer_cfg" ]] && grep -q "klipper_tft_macros.cfg" "$printer_cfg"; then
                echo ""
                read -p "Remove include line from printer.cfg? (y/N): " -r
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    # Create backup
                    cp "$printer_cfg" "${printer_cfg}.backup.$(date +%Y%m%d_%H%M%S)"
                    
                    # Remove include lines
                    sed -i '/\[include klipper_tft_macros\.cfg\]/d' "$printer_cfg"
                    sed -i '/klipper_tft_macros\.cfg/d' "$printer_cfg"
                    
                    print_success "Removed include line from printer.cfg"
                    print_info "Backup created: ${printer_cfg}.backup.*"
                    print_warning "You should restart Klipper to reload configuration"
                else
                    print_info "Include line preserved in printer.cfg"
                fi
            fi
        else
            print_info "Klipper macro file preserved"
        fi
    else
        print_info "No Klipper macro file found"
    fi
}

remove_virtual_environment() {
    print_step "Virtual environment removal..."
    
    local venv_locations=(
        "${BRIDGE_BASE_DIR}/.tft-bridge-venv"
        "${BRIDGE_INSTALL_DIR}/.tft-bridge-venv"
    )
    
    local found_venv=false
    for venv_dir in "${venv_locations[@]}"; do
        if [[ -d "$venv_dir" ]]; then
            found_venv=true
            break
        fi
    done
    
    if [[ "$found_venv" == "true" ]]; then
        echo ""
        read -p "Remove TFT bridge virtual environment? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for venv_dir in "${venv_locations[@]}"; do
                if [[ -d "$venv_dir" ]]; then
                    rm -rf "$venv_dir"
                    print_success "Removed virtual environment: $venv_dir"
                fi
            done
        else
            print_info "Virtual environment preserved"
        fi
    else
        print_info "No virtual environment found"
    fi
}

remove_installation_directory() {
    print_step "Installation directory cleanup..."
    
    if [[ -d "$BRIDGE_INSTALL_DIR" ]]; then
        # Check if directory is empty or only contains hidden files
        if [[ -z "$(ls -A "$BRIDGE_INSTALL_DIR" 2>/dev/null)" ]]; then
            echo ""
            read -p "Remove empty installation directory? (y/N): " -r
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rmdir "$BRIDGE_INSTALL_DIR" 2>/dev/null && print_success "Removed installation directory: $BRIDGE_INSTALL_DIR" || print_warning "Could not remove installation directory (may not be empty)"
            else
                print_info "Installation directory preserved"
            fi
        else
            print_info "Installation directory contains files - preserved"
        fi
    else
        print_info "Installation directory not found"
    fi
}

kill_running_processes() {
    print_step "Checking for running bridge processes..."
    
    local processes=$(ps aux | grep "tft_moonraker_bridge" | grep -v grep | awk '{print $2}')
    
    if [[ -n "$processes" ]]; then
        print_warning "Found running bridge processes"
        echo "PIDs: $processes"
        
        read -p "Kill running processes? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "$processes" | xargs -r sudo kill -TERM
            sleep 2
            
            # Check if still running, force kill if needed
            local remaining=$(ps aux | grep "tft_moonraker_bridge" | grep -v grep | awk '{print $2}')
            if [[ -n "$remaining" ]]; then
                echo "$remaining" | xargs -r sudo kill -9
                print_warning "Force killed remaining processes"
            fi
            print_success "Bridge processes terminated"
        else
            print_warning "Processes left running"
        fi
    else
        print_info "No running bridge processes found"
    fi
}

verify_removal() {
    print_step "Verifying removal..."
    
    local issues=0
    
    # Check service
    if systemctl list-unit-files | grep -q "^${SERVICE_NAME}\.service"; then
        print_error "Service still exists in systemd"
        ((issues++))
    else
        print_success "Service removed from systemd"
    fi
    
    # Check service file
    if [[ -f "/etc/systemd/system/${SERVICE_NAME}.service" ]]; then
        print_error "Service file still exists"
        ((issues++))
    else
        print_success "Service file removed"
    fi
    
    # Check for running processes
    if ps aux | grep -q "[t]ft_moonraker_bridge"; then
        print_warning "Bridge processes still running"
        ((issues++))
    else
        print_success "No bridge processes running"
    fi
    
    return $issues
}

show_summary() {
    echo ""
    echo -e "${CYAN}=============================================="
    echo "            Uninstall Summary"
    echo "===============================================${NC}"
    echo ""
    
    echo -e "${GREEN}✓ Removed:${NC}"
    echo "  • TFT bridge systemd service"
    echo "  • Service configuration"
    echo "  • Helper scripts"
    echo "  • Log files"
    echo ""
    
    echo -e "${BLUE}ℹ Preserved (if they exist):${NC}"
    echo "  • Bridge source code (unless you chose to remove)"
    echo "  • Klipper macros (unless you chose to remove)"
    echo "  • Virtual environment (unless you chose to remove)"
    echo ""
    
    echo -e "${YELLOW}⚠ Manual cleanup (if needed):${NC}"
    echo "  • Remove any custom modifications you made"
    echo "  • Check printer.cfg for any remaining TFT references"
    echo "  • Restart Klipper if you removed macros"
    echo ""
    
    echo -e "${GREEN}TFT bridge uninstall completed successfully!${NC}"
}

main() {
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
    
    print_header
    confirm_removal
    
    # Core removal steps
    kill_running_processes
    stop_and_disable_service
    remove_service_file
    remove_helper_scripts
    remove_log_files
    
    # Optional removal steps
    optional_remove_bridge_script
    optional_remove_klipper_macros
    remove_virtual_environment
    remove_installation_directory
    
    # Verification
    if verify_removal; then
        show_summary
    else
        echo ""
        print_warning "Some issues were found during verification"
        print_info "You may need to manually clean up remaining items"
    fi
}

# Script usage help
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "TFT-Moonraker Bridge Uninstall Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --force        Skip confirmation prompts (use with caution)"
    echo ""
    echo "This script removes:"
    echo "  • TFT bridge systemd service"
    echo "  • Service configuration files"
    echo "  • Helper scripts and log files"
    echo "  • Optionally: bridge scripts, Klipper macros, virtual environment"
    echo ""
    exit 0
fi

# Force mode
if [[ "$1" == "--force" ]]; then
    print_header
    print_warning "Force mode enabled - minimal prompts"
    echo ""
else
    main
fi