#!/bin/bash
# Installation script for KCamera Controls

set -e

echo "Installing KCamera Controls..."

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    DISTRO_LIKE=$ID_LIKE
else
    echo "Error: Cannot detect Linux distribution."
    exit 1
fi

echo "Detected distribution: $DISTRO"

# Function to check if we're on a Fedora-based system
is_fedora_based() {
    [[ "$DISTRO" == "fedora" ]] || [[ "$DISTRO" == "rhel" ]] || [[ "$DISTRO" == "centos" ]] || [[ "$DISTRO_LIKE" == *"fedora"* ]]
}

# Function to check if we're on a Debian-based system
is_debian_based() {
    [[ "$DISTRO" == "debian" ]] || [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO_LIKE" == *"debian"* ]]
}

# Function to install packages based on distribution
install_package() {
    local package=$1
    
    if is_fedora_based; then
        echo "Installing $package using dnf..."
        sudo dnf install -y "$package"
    elif is_debian_based; then
        echo "Installing $package using apt..."
        sudo apt-get update -qq
        sudo apt-get install -y "$package"
    else
        echo "Warning: Unsupported distribution. Please install $package manually."
        return 1
    fi
}

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Installing..."
    install_package python3
else
    echo "Python 3 found: $(python3 --version)"
fi

# Check for pip3
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Installing..."
    install_package python3-pip
else
    echo "pip3 found: $(pip3 --version)"
fi

# Check for v4l2-ctl
if ! command -v v4l2-ctl &> /dev/null; then
    echo "v4l2-ctl not found. Installing v4l-utils..."
    install_package v4l-utils
else
    echo "v4l2-ctl found"
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
