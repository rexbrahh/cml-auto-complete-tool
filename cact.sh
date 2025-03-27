#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# If the script is a symlink, get the actual directory
if [ -L "${BASH_SOURCE[0]}" ]; then
    SCRIPT_DIR="$( cd "$( dirname "$(readlink -f "${BASH_SOURCE[0]}")" )" && pwd )"
fi

# Create a virtual environment in the user's home directory
VENV_DIR="$HOME/.cact-venv"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    "$1" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'
}

# Function to find Python 3.9
find_python3_9() {
    # Common locations for Python 3.9
    PYTHON_LOCATIONS=(
        "/usr/local/bin/python3.9"
        "/usr/bin/python3.9"
        "/opt/homebrew/bin/python3.9"
        "/usr/local/opt/python@3.9/bin/python3.9"
        "$HOME/.pyenv/versions/3.9.*/bin/python3.9"
    )
    
    for location in "${PYTHON_LOCATIONS[@]}"; do
        if [ -f "$location" ]; then
            echo "$location"
            return 0
        fi
    done
    
    # Try to find using which
    if command_exists python3.9; then
        which python3.9
        return 0
    fi
    
    return 1
}

# Function to create and setup virtual environment
setup_venv() {
    echo "Setting up virtual environment..."
    
    # Try to find Python 3.9
    PYTHON_3_9=$(find_python3_9)
    if [ -n "$PYTHON_3_9" ]; then
        echo "Found Python 3.9 at: $PYTHON_3_9"
        PYTHON_CMD="$PYTHON_3_9"
    else
        echo "Warning: Python 3.9 not found, falling back to system Python"
        PYTHON_CMD="python3"
    fi
    
    # Remove existing venv if it exists
    if [ -d "$VENV_DIR" ]; then
        echo "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    
    # Create new venv
    echo "Creating new virtual environment with: $PYTHON_CMD"
    if ! "$PYTHON_CMD" -m venv "$VENV_DIR"; then
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
    
    # Install dependencies from requirements.txt
    echo "Installing dependencies from requirements.txt..."
    if ! pip install -r "$SCRIPT_DIR/requirements.txt"; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
    
    # Install the package
    echo "Installing package from: $SCRIPT_DIR"
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
PYTHON_VERSION=$(get_python_version python3)
echo "System Python version: $PYTHON_VERSION"

# Check if virtual environment exists and is valid
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
    setup_venv
fi

# Try to activate the virtual environment
if ! source "$VENV_DIR/bin/activate"; then
    echo "Error: Virtual environment is corrupted. Recreating..."
    setup_venv
fi

# Run the command using the Python module directly
python -m cml_auto_complete_tool.cli "$@" 