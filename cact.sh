#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create a virtual environment in the user's home directory
VENV_DIR="$HOME/.cact-venv"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create and setup virtual environment
setup_venv() {
    echo "Setting up virtual environment..."
    if ! python3 -m venv "$VENV_DIR"; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
    
    # Activate virtual environment and install/upgrade the package
    if ! source "$VENV_DIR/bin/activate" && pip install --upgrade pip && pip install -e "$SCRIPT_DIR"; then
        echo "Error: Failed to install required packages"
        exit 1
    fi
}

# Check if Python is installed
if ! command_exists python3; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists and is valid
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
    setup_venv
fi

# Try to activate the virtual environment
if ! source "$VENV_DIR/bin/activate"; then
    echo "Error: Virtual environment is corrupted. Recreating..."
    rm -rf "$VENV_DIR"
    setup_venv
fi

# Run the command with all arguments passed through
cact "$@" 