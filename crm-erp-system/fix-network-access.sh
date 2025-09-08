#!/bin/bash

# Fix Network Access Script
set -euo pipefail

echo "🌐 Fixing Network Access for CRM/ERP System"
echo "==========================================="
echo

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

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
print_status "Server IP: $SERVER_IP"

# Stop existing services
print_status "Stopping existing services..."
pkill -f "python manage.py runserver" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
sleep 3

# Start Django on all interfaces
print_status "Starting Django on all interfaces..."
cd backend
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
echo $! > django.pid

# Wait for Django
print_status "Waiting for Django to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/admin/ >/dev/null 2>&1; then
        print_success "Django server is running on all interfaces"
        break
    fi
    sleep 2
done

# Start React with host binding
print_status "Starting React with network access..."
cd ../frontend

# Set HOST environment variable for React
export HOST=0.0.0.0
nohup npm start > react.log 2>&1 &
echo $! > react.pid

# Wait for React
print_status "Waiting for React to start..."
for i in {1..60}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_success "React server is running on all interfaces"
        break
    fi
    sleep 2
done

# Check firewall
print_status "Checking firewall status..."
if command -v ufw &> /dev/null; then
    print_status "Configuring UFW firewall..."
    sudo ufw allow 8000/tcp
    sudo ufw allow 3000/tcp
    print_success "Firewall configured"
fi

# Show access URLs
echo
print_success "🎉 Network Access Fixed!"
echo "============================="
echo
echo "🌐 Access URLs:"
echo "   Frontend: http://$SERVER_IP:3000"
echo "   Backend:  http://$SERVER_IP:8000"
echo "   Admin:    http://$SERVER_IP:8000/admin"
echo
echo "🔑 Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo
echo "📱 From other devices on the same network:"
echo "   Use the IP address above instead of localhost"
echo
print_success "System is now accessible from the network!"