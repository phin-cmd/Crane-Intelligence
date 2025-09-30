#!/bin/bash
# Linux/macOS startup script for Crane Intelligence Platform
echo "Starting Crane Intelligence Platform on $(uname -s)..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Start the platform using Python script
echo "Starting platform..."
python start_platform.py
