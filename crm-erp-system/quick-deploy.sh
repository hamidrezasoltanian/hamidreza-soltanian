#!/bin/bash

# Quick Deploy Script - Handles Python externally managed environment
set -euo pipefail

echo "🚀 Quick CRM/ERP Deploy Script"
echo "=============================="
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

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Kill existing processes
print_status "Stopping existing processes..."
pkill -f "python manage.py runserver" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
sleep 2

# Check Node.js
print_status "Checking Node.js installation..."
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    print_warning "Node.js or npm not found. Installing..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

print_status "Node.js version: $(node --version)"
print_status "npm version: $(npm --version)"

# Setup Backend
print_status "Setting up Backend..."
cd "$BACKEND_DIR"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies with proper flags
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup database
print_status "Setting up database..."
sudo systemctl start postgresql 2>/dev/null || true

# Create .env file if not exists
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
DEBUG=True
SECRET_KEY=your-secret-key-$(date +%s)
DB_NAME=crm_erp
DB_USER=postgres
DB_PASSWORD=62604193
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
EOF
fi

# Run migrations
print_status "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create admin user
print_status "Creating admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created')
else:
    print('Admin user already exists')
"

# Start Django
print_status "Starting Django server..."
nohup python manage.py runserver 0.0.0.0:8000 > "$BACKEND_DIR/django.log" 2>&1 &
echo $! > "$BACKEND_DIR/django.pid"

# Wait for Django to start
print_status "Waiting for Django to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/admin/ >/dev/null 2>&1; then
        print_success "Django server is running on http://localhost:8000"
        break
    fi
    sleep 2
done

# Setup Frontend
print_status "Setting up Frontend..."
cd "$FRONTEND_DIR"

# Clean install
print_status "Installing Node.js dependencies..."
rm -rf node_modules package-lock.json 2>/dev/null || true
npm cache clean --force 2>/dev/null || true
npm install

# Start React
print_status "Starting React server..."
nohup npm start > "$FRONTEND_DIR/react.log" 2>&1 &
echo $! > "$FRONTEND_DIR/react.pid"

# Wait for React to start
print_status "Waiting for React to start..."
for i in {1..60}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_success "React server is running on http://localhost:3000"
        break
    fi
    sleep 2
done

# Create helper scripts
print_status "Creating helper scripts..."

# Stop script
cat > "$SCRIPT_DIR/stop.sh" << 'EOF'
#!/bin/bash
echo "🛑 Stopping CRM/ERP System..."
pkill -f "python manage.py runserver" || true
pkill -f "npm start" || true
pkill -f "react-scripts start" || true
echo "✅ All services stopped"
EOF

# Test script
cat > "$SCRIPT_DIR/test.sh" << 'EOF'
#!/bin/bash
echo "🧪 Testing CRM/ERP System..."
curl -sSf http://localhost:8000/admin/ >/dev/null && echo "✅ Backend OK" || echo "❌ Backend not responding"
curl -sSf http://localhost:3000 >/dev/null && echo "✅ Frontend OK" || echo "❌ Frontend not responding"
EOF

chmod +x "$SCRIPT_DIR"/*.sh

# Show final status
echo
print_success "🎉 CRM/ERP System Deployed Successfully!"
echo "=============================================="
echo
echo "🌐 Frontend (React): http://localhost:3000"
echo "🔧 Backend (Django): http://localhost:8000"
echo "👤 Admin Panel: http://localhost:8000/admin"
echo "📊 API Base: http://localhost:8000/api/v1/"
echo
echo "🔑 Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo
echo "🛠️ Management Commands:"
echo "   Stop: ./stop.sh"
echo "   Test: ./test.sh"
echo
print_success "System is ready to use!"