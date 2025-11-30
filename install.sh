#!/bin/bash
# Installation script for KCamera Controls

set -e

echo "Installing KCamera Controls..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check for v4l2-ctl
if ! command -v v4l2-ctl &> /dev/null; then
    echo "Warning: v4l2-ctl not found. Installing v4l-utils..."
    sudo apt-get update
    sudo apt-get install -y v4l-utils
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Install application
echo "Installing application files..."
sudo cp kcameracontrols.py /usr/local/bin/kcameracontrols
sudo chmod +x /usr/local/bin/kcameracontrols

# Copy directories
sudo mkdir -p /usr/local/share/kcameracontrols
sudo cp -r ui backend /usr/local/share/kcameracontrols/

# Install desktop entry
echo "Installing desktop entry..."
sudo cp kcameracontrols.desktop /usr/share/applications/

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    sudo update-desktop-database /usr/share/applications
fi

echo ""
echo "Installation complete!"
echo "You can now:"
echo "  1. Launch from your application menu"
echo "  2. Run 'kcameracontrols' from the command line"
echo "  3. Add to autostart in KDE System Settings"
