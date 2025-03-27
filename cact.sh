#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create a virtual environment in the user's home directory
VENV_DIR="$HOME/.cact-venv"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment and install/upgrade the package
source "$VENV_DIR/bin/activate" && \
pip install --upgrade pip && \
pip install -e "$SCRIPT_DIR"

# Run the command with all arguments passed through
cact "$@" 