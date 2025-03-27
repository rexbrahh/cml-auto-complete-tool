#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create a virtual environment in the user's home directory
VENV_DIR="$HOME/.cact-venv"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'
}

# Function to create and setup virtual environment
setup_venv() {
    echo "Setting up virtual environment..."
    
    # Try to use Python 3.9 if available (more stable for venv)
    PYTHON_CMD="python3"
    if command_exists python3.9; then
        PYTHON_CMD="python3.9"
        echo "Using Python 3.9 for better compatibility..."
    fi
    
    # Remove existing venv if it exists
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
    fi
    
    # Create new venv
    if ! $PYTHON_CMD -m venv "$VENV_DIR"; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
    
    # Activate virtual environment
    if ! source "$VENV_DIR/bin/activate"; then
        echo "Error: Failed to activate virtual environment"
        exit 1
    fi
    
    # Upgrade pip and install wheel
    echo "Upgrading pip and installing wheel..."
    if ! pip install --upgrade pip wheel setuptools; then
        echo "Error: Failed to upgrade pip and install wheel"
        exit 1
    fi
    
    # Install the package
    echo "Installing package..."
    if ! pip install -e "$SCRIPT_DIR"; then
        echo "Error: Failed to install required packages"
        exit 1
    fi
}

# Check if Python is installed
if ! command_exists python3; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(get_python_version)
echo "Using Python version: $PYTHON_VERSION"

# Check if virtual environment exists and is valid
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
    setup_venv
fi

# Try to activate the virtual environment
if ! source "$VENV_DIR/bin/activate"; then
    echo "Error: Virtual environment is corrupted. Recreating..."
    setup_venv
fi

# Run the command with all arguments passed through
cact "$@" 