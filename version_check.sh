#!/bin/bash

# TFT Bridge Version Management Script
# Provides easy access to version information and checking

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

print_usage() {
    echo "TFT Bridge Version Management"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  info           Show current version information"
    echo "  history        Show version history"
    echo "  check [VER]    Show specific version details"
    echo "  file           Show version from VERSION file"
    echo "  compare        Compare script vs file versions"
    echo "  all            Show all version information"
    echo ""
    echo "Examples:"
    echo "  $0 info        # Current version info"
    echo "  $0 history     # Full changelog"
    echo "  $0 check 2.0.0 # Details for v2.0.0"
    echo "  $0 all         # Everything"
    echo ""
}

get_script_version() {
    if [[ -f "tft_moonraker_bridge.py" ]]; then
        grep "^__version__" tft_moonraker_bridge.py | cut -d'"' -f2
    else
        echo "Unknown (script not found)"
    fi
}

get_file_version() {
    if [[ -f "VERSION" ]]; then
        cat VERSION | tr -d '\n\r'
    else
        echo "Unknown (VERSION file not found)"
    fi
}

show_version_info() {
    echo -e "${CYAN}=== TFT Bridge Version Information ===${NC}"
    echo ""
    
    if [[ -f "show_version.py" ]]; then
        python3 show_version.py
    elif [[ -f "tft_moonraker_bridge.py" ]]; then
        python3 tft_moonraker_bridge.py --version 2>/dev/null || {
            echo -e "${YELLOW}Dependencies not installed, showing basic info:${NC}"
            echo "Script version: $(get_script_version)"
        }
    else
        echo -e "${RED}Bridge script not found!${NC}"
    fi
    
    echo ""
    echo "File version: $(get_file_version)"
}

show_version_history() {
    echo -e "${CYAN}=== TFT Bridge Version History ===${NC}"
    echo ""
    
    if [[ -f "tft_moonraker_bridge.py" ]]; then
        python3 tft_moonraker_bridge.py --version-history 2>/dev/null || {
            echo -e "${RED}Failed to get version history from script${NC}"
            echo "Check CHANGELOG.md for detailed history"
        }
    else
        echo -e "${RED}Bridge script not found!${NC}"
        echo "Check CHANGELOG.md for version history"
    fi
}

check_specific_version() {
    local version="$1"
    echo -e "${CYAN}=== Version $version Details ===${NC}"
    echo ""
    
    if [[ -f "tft_moonraker_bridge.py" ]]; then
        python3 tft_moonraker_bridge.py --version-info "$version" 2>/dev/null || {
            echo -e "${RED}Failed to get version details from script${NC}"
            echo "Check CHANGELOG.md for version $version details"
        }
    else
        echo -e "${RED}Bridge script not found!${NC}"
    fi
}

compare_versions() {
    local script_ver=$(get_script_version)
    local file_ver=$(get_file_version)
    
    echo -e "${CYAN}=== Version Comparison ===${NC}"
    echo ""
    echo "Script version: $script_ver"
    echo "File version:   $file_ver"
    echo ""
    
    if [[ "$script_ver" == "$file_ver" ]]; then
        echo -e "${GREEN}✓ Versions match${NC}"
    else
        echo -e "${YELLOW}⚠ Version mismatch detected${NC}"
        echo "The script and VERSION file have different versions"
        echo "This may indicate an incomplete update"
    fi
}

show_all_info() {
    show_version_info
    echo ""
    compare_versions
    echo ""
    
    if [[ -f "CHANGELOG.md" ]]; then
        echo -e "${BLUE}Recent changes (see CHANGELOG.md for full history):${NC}"
        head -20 CHANGELOG.md | tail -15
    fi
}

# Main script logic
case "${1:-info}" in
    info|--info|-i)
        show_version_info
        ;;
    history|--history|-h)
        show_version_history
        ;;
    check|--check|-c)
        if [[ -n "$2" ]]; then
            check_specific_version "$2"
        else
            echo "Error: Please specify a version number"
            echo "Example: $0 check 2.0.0"
            exit 1
        fi
        ;;
    file|--file|-f)
        echo "VERSION file: $(get_file_version)"
        ;;
    compare|--compare)
        compare_versions
        ;;
    all|--all|-a)
        show_all_info
        ;;
    help|--help)
        print_usage
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        print_usage
        exit 1
        ;;
esac