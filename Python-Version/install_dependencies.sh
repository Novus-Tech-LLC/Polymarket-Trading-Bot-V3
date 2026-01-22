#!/bin/bash
# Install dependencies for Polymarket Copy Trading Bot
# This script works in Git Bash, WSL, and Linux/Mac

echo "========================================"
echo "Installing Dependencies"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    echo ""
    echo "Please install Python 3.9+ first:"
    echo "  Windows: Use Microsoft Store or download from python.org"
    echo "  Make sure to check 'Add Python to PATH' during installation"
    echo ""
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo "✓ Found Python: $($PYTHON_CMD --version)"
echo ""

# Check if pip is available
if ! command -v $PIP_CMD &> /dev/null && ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "❌ pip is not available"
    echo ""
    echo "Installing pip..."
    $PYTHON_CMD -m ensurepip --upgrade
    if [ $? -ne 0 ]; then
        echo "Failed to install pip. Please install pip manually."
        exit 1
    fi
fi

# Use python -m pip if pip command not found
if ! command -v $PIP_CMD &> /dev/null; then
    PIP_CMD="$PYTHON_CMD -m pip"
    echo "Using: $PIP_CMD"
else
    echo "✓ Found pip: $($PIP_CMD --version)"
fi

echo ""
echo "Installing dependencies from requirements.txt..."
echo ""

# Install dependencies
$PIP_CMD install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Create .env file with your configuration"
    echo "  2. Run the bot: $PYTHON_CMD -m src.main"
    echo ""
else
    echo ""
    echo "❌ Failed to install dependencies"
    echo ""
    echo "Try running manually:"
    echo "  $PIP_CMD install -r requirements.txt"
    echo ""
    exit 1
fi
