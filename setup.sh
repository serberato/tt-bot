#!/bin/bash
MAIN_SCRIPT="main.py"
REQUIREMENTS_FILE="requirements-linux.txt"
SDK_DOWNLOADER_SCRIPT="downloader.py"

set -e
cd "$(dirname "$0")"

C_GREEN='\033[0;32m'
C_RED='\033[0;31m'
C_YELLOW='\033[0;33m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

print_step() {
    echo -e "\n${C_BOLD}${C_GREEN}>> Step ${1}:${C_RESET}${C_BOLD} ${2}${C_RESET}"
}

# Prints a success message
print_success() {
    echo -e "${C_GREEN}✔ ${1}${C_RESET}"
}

# Prints an error message and exits
print_error() {
    echo -e "\n${C_RED}✖ ERROR: ${1}${C_RESET}"
    echo -e "${C_YELLOW}Setup cannot continue. Please fix the issue and run the script again.${C_RESET}"
    exit 1
}

main() {
    clear
    echo -e "${C_BOLD}Welcome to the TT Utilities Bot Setup${C_RESET}"
    echo
    echo "This script will check for required software, install any missing components,"
    echo "and configure the bot for you."
    echo
    read -p "Press [Enter] to begin the setup..."
    clear

    print_step "1 of 6" "Checking system dependencies..."
    if [ ! -f /etc/os-release ]; then
        print_error "Cannot determine Linux distribution. /etc/os-release not found."
    fi
    # shellcheck source=/dev/null
    . /etc/os-release
    if [[ "$ID" == "debian" || "$ID" == "ubuntu" ]]; then
        PACKAGES="python3 python3-dev python3-pip git p7zip-full"
        echo "Updating package list..."
        sudo apt-get update -qq
        echo "Installing: ${PACKAGES}..."
        sudo apt-get install -y -qq ${PACKAGES}
        print_success "System dependencies are installed."
    else
        echo -e "${C_YELLOW}Warning: Non-Debian based distribution ('${ID}') detected.${C_RESET}"
        echo "Please ensure the following packages (or equivalents) are installed:"
        echo "python3, pip, git, 7zip"
        read -p "Press [Enter] to continue if they are installed, or Ctrl+C to exit."
    fi

    print_step "2 of 6" "Installing Python libraries..."
    if [ ! -f "${REQUIREMENTS_FILE}" ]; then
        print_error "'${REQUIREMENTS_FILE}' not found."
    fi
    echo "This may take a few moments..."
    if ! python3 -m pip install -r "${REQUIREMENTS_FILE}" -q --no-input; then
        print_error "Failed to install Python libraries. Try running 'pip3 install -r ${REQUIREMENTS_FILE}' manually."
    fi
    print_success "Python libraries installed successfully."

    print_step "3 of 6" "Checking Deno installation..."
    if command -v deno >/dev/null 2>&1; then
        print_success "Deno is already installed and found in PATH."
    else
        echo "Deno not found. Installing Deno..."
        if ! curl -fsSL https://deno.land/install.sh | sh; then
            print_error "Failed to install Deno."
        fi
    fi

    print_step "4 of 6" "Configuring the TeamTalk SDK..."
    if [ ! -f "${SDK_DOWNLOADER_SCRIPT}" ]; then
        print_error "SDK downloader script ('${SDK_DOWNLOADER_SCRIPT}') not found."
    fi
    if ! python3 "${SDK_DOWNLOADER_SCRIPT}"; then
        print_error "The TeamTalk SDK download script failed."
    fi
    print_success "TeamTalk SDK configured successfully."

    print_step "5 of 5" "Finalizing installation..."
    echo "The TeamTalk SDK is now configured to load locally from the TeamTalk_DLL folder."
    print_success "Installation finalized without requiring root privileges."

    echo
    echo -e "  Setup is Complete!"
    echo
    echo "The bot is now ready to be launched."
    echo "You can start it by running the following command:"
    echo -e "  ${C_YELLOW}python3 ${MAIN_SCRIPT}${C_RESET}"
    echo
}

main "$@"
