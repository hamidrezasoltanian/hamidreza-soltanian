#!/bin/bash

# Fix Node.js and npm conflicts
set -euo pipefail

echo "🔧 Fixing Node.js and npm conflicts..."
echo "====================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Remove conflicting packages
print_status "Removing conflicting Node.js packages..."
sudo apt-get remove --purge -y nodejs npm nodejs-doc || true
sudo apt-get autoremove -y

# Clean package cache
print_status "Cleaning package cache..."
sudo apt-get clean
sudo apt-get autoclean

# Add NodeSource repository for latest Node.js
print_status "Adding NodeSource repository..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Install Node.js and npm
print_status "Installing Node.js and npm..."
sudo apt-get install -y nodejs

# Verify installation
print_status "Verifying installation..."
node --version
npm --version

print_success "Node.js and npm fixed successfully!"

# Install global packages if needed
print_status "Installing global packages..."
npm install -g npm@latest

print_success "🎉 Node.js setup completed!"