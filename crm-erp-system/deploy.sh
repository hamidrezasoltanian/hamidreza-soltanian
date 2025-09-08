#!/bin/bash

# Enhanced Auto-Deploy Script for CRM/ERP System
# - Always pulls latest from GitHub
# - Completely cleans previous installations
# - Sets up fresh environment
# - Auto-starts services

set -euo pipefail

echo "🚀 Enhanced CRM/ERP Auto-Deploy Script"
echo "======================================"
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

# Configuration
REPO_URL="https://github.com/hamidrezasoltanian/hamidreza-soltanian.git"
BRANCH_NAME="main"
PROJECT_NAME="crm-erp-system"
INSTALL_DIR="/opt/crm-erp"
BACKUP_DIR="/opt/crm-erp-backup-$(date +%Y%m%d-%H%M%S)"

# Clean installation function
clean_install() {
  print_step "🧹 Cleaning previous installation..."
  
  # Stop all services
  print_status "Stopping existing services..."
  pkill -f "python manage.py runserver" 2>/dev/null || true
  pkill -f "npm start" 2>/dev/null || true
  pkill -f "react-scripts start" 2>/dev/null || true
  pkill -f "node.*3000" 2>/dev/null || true
  pkill -f "python.*8000" 2>/dev/null || true
  
  # Free ports
  command -v fuser >/dev/null 2>&1 && fuser -k 8000/tcp 2>/dev/null || true
  command -v fuser >/dev/null 2>&1 && fuser -k 3000/tcp 2>/dev/null || true
  
  sleep 3
  
  # Backup existing installation if it exists
  if [ -d "$INSTALL_DIR" ]; then
    print_status "Backing up existing installation to $BACKUP_DIR..."
    mv "$INSTALL_DIR" "$BACKUP_DIR" || true
  fi
  
  # Clean system packages
  print_status "Cleaning system packages..."
  sudo apt-get update -qq
  sudo apt-get install -y git curl wget python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib
  
  # Clean npm cache
  npm cache clean --force 2>/dev/null || true
  
  # Clean pip cache
  pip cache purge 2>/dev/null || true
  
  print_success "Cleanup completed"
}

# Clone fresh repository
clone_fresh() {
  print_step "📥 Cloning fresh repository..."
  
  # Create install directory
  sudo mkdir -p "$INSTALL_DIR"
  sudo chown $USER:$USER "$INSTALL_DIR"
  
  # Clone repository
  cd /tmp
  rm -rf "$PROJECT_NAME" 2>/dev/null || true
  git clone --branch "$BRANCH_NAME" --depth 1 "$REPO_URL" "$PROJECT_NAME"
  
  # Move to install directory
  cp -r "$PROJECT_NAME"/* "$INSTALL_DIR/"
  cd "$INSTALL_DIR"
  
  # Set proper permissions
  chmod +x deploy.sh quick-deploy.sh stop.sh test.sh 2>/dev/null || true
  
  print_success "Repository cloned to $INSTALL_DIR"
}

# Setup backend
setup_backend() {
  print_step "🐍 Setting up Backend (Django)..."
  cd "$INSTALL_DIR/backend"
  
  # Create virtual environment
  print_status "Creating Python virtual environment..."
  python3 -m venv venv
  source venv/bin/activate
  
  # Upgrade pip
  pip install --upgrade pip setuptools wheel
  
  # Install dependencies
  print_status "Installing Python dependencies..."
  pip install -r requirements.txt
  
  # Setup PostgreSQL
  print_status "Setting up PostgreSQL..."
  sudo systemctl start postgresql
  sudo systemctl enable postgresql
  
  # Create database user and database
  sudo -u postgres psql -c "CREATE USER crm_user WITH PASSWORD 'crm_password';" 2>/dev/null || true
  sudo -u postgres psql -c "CREATE DATABASE crm_erp OWNER crm_user;" 2>/dev/null || true
  sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE crm_erp TO crm_user;" 2>/dev/null || true
  
  # Create .env file
  cat > .env << EOF
DEBUG=True
SECRET_KEY=your-secret-key-here-$(date +%s)
DB_NAME=crm_erp
DB_USER=crm_user
DB_PASSWORD=crm_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
EOF
  
  # Run migrations
  print_status "Running database migrations..."
  python manage.py makemigrations
  python manage.py migrate
  
  # Create superuser
  print_status "Creating admin user..."
  python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created')
else:
    print('Admin user already exists')
"
  
  print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
  print_step "⚛️ Setting up Frontend (React)..."
  cd "$INSTALL_DIR/frontend"
  
  # Clean install
  print_status "Installing Node.js dependencies..."
  rm -rf node_modules package-lock.json 2>/dev/null || true
  npm cache clean --force
  npm install
  
  print_success "Frontend setup completed"
}

# Start services
start_services() {
  print_step "🚀 Starting services..."
  
  # Start Django backend
  print_status "Starting Django server..."
  cd "$INSTALL_DIR/backend"
  source venv/bin/activate
  nohup python manage.py runserver 0.0.0.0:8000 > "$INSTALL_DIR/backend/django.log" 2>&1 &
  echo $! > "$INSTALL_DIR/backend/django.pid"
  
  # Wait for Django to start
  print_status "Waiting for Django to start..."
  for i in {1..30}; do
    if curl -s http://localhost:8000/admin/ >/dev/null 2>&1; then
      print_success "Django server is running on http://localhost:8000"
      break
    fi
    sleep 2
    if [ $i -eq 30 ]; then
      print_warning "Django server might not be ready yet"
    fi
  done
  
  # Start React frontend
  print_status "Starting React server..."
  cd "$INSTALL_DIR/frontend"
  nohup npm start > "$INSTALL_DIR/frontend/react.log" 2>&1 &
  echo $! > "$INSTALL_DIR/frontend/react.pid"
  
  # Wait for React to start
  print_status "Waiting for React to start..."
  for i in {1..60}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
      print_success "React server is running on http://localhost:3000"
      break
    fi
    sleep 2
    if [ $i -eq 60 ]; then
      print_warning "React server might not be ready yet"
    fi
  done
  
  print_success "All services started"
}

# Create management scripts
create_scripts() {
  print_step "📝 Creating management scripts..."
  
  # Stop script
  cat > "$INSTALL_DIR/stop.sh" << 'EOF'
#!/bin/bash
set -e
echo "🛑 Stopping CRM/ERP System..."
INSTALL_DIR="/opt/crm-erp"

if [ -f "$INSTALL_DIR/backend/django.pid" ]; then
  kill "$(cat "$INSTALL_DIR/backend/django.pid")" 2>/dev/null || true
  rm -f "$INSTALL_DIR/backend/django.pid"
  echo "✅ Django server stopped"
fi

if [ -f "$INSTALL_DIR/frontend/react.pid" ]; then
  kill "$(cat "$INSTALL_DIR/frontend/react.pid")" 2>/dev/null || true
  rm -f "$INSTALL_DIR/frontend/react.pid"
  echo "✅ React server stopped"
fi

pkill -f "python manage.py runserver" || true
pkill -f "npm start" || true
pkill -f "react-scripts start" || true
echo "✅ All services stopped"
EOF

  # Quick restart script
  cat > "$INSTALL_DIR/restart.sh" << 'EOF'
#!/bin/bash
set -e
echo "⚡ Quick Restart - Restarting Services..."
INSTALL_DIR="/opt/crm-erp"

# Stop services
pkill -f "python manage.py runserver" || true
pkill -f "npm start" || true
pkill -f "react-scripts start" || true
sleep 3

# Start Django
cd "$INSTALL_DIR/backend"
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8000 > "$INSTALL_DIR/backend/django.log" 2>&1 &
echo $! > "$INSTALL_DIR/backend/django.pid"

# Start React
cd "$INSTALL_DIR/frontend"
nohup npm start > "$INSTALL_DIR/frontend/react.log" 2>&1 &
echo $! > "$INSTALL_DIR/frontend/react.pid"

echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "👤 Admin: http://localhost:8000/admin"
echo "🔑 Login: admin / admin123"
EOF

  # Test script
  cat > "$INSTALL_DIR/test.sh" << 'EOF'
#!/bin/bash
set -e
echo "🧪 Testing CRM/ERP System..."

# Test backend
if curl -sSf http://localhost:8000/admin/ >/dev/null 2>&1; then
  echo "✅ Backend OK - Django is running"
else
  echo "❌ Backend not responding"
fi

# Test frontend
if curl -sSf http://localhost:3000 >/dev/null 2>&1; then
  echo "✅ Frontend OK - React is running"
else
  echo "❌ Frontend not responding"
fi

# Test API
if curl -sSf http://localhost:8000/api/v1/ >/dev/null 2>&1; then
  echo "✅ API OK - REST API is accessible"
else
  echo "❌ API not responding"
fi
EOF

  # Auto-update script
  cat > "$INSTALL_DIR/update.sh" << 'EOF'
#!/bin/bash
set -e
echo "🔄 Auto-Updating CRM/ERP System..."
INSTALL_DIR="/opt/crm-erp"

# Stop services
echo "Stopping services..."
pkill -f "python manage.py runserver" || true
pkill -f "npm start" || true
pkill -f "react-scripts start" || true
sleep 3

# Update code
echo "Updating code from GitHub..."
cd "$INSTALL_DIR"
git fetch origin
git reset --hard origin/main
git clean -fd

# Update backend
echo "Updating backend..."
cd "$INSTALL_DIR/backend"
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

# Update frontend
echo "Updating frontend..."
cd "$INSTALL_DIR/frontend"
npm install

# Restart services
echo "Restarting services..."
cd "$INSTALL_DIR"
./restart.sh

echo "✅ Update completed!"
EOF

  chmod +x "$INSTALL_DIR"/*.sh
  
  print_success "Management scripts created:"
  echo "  - stop.sh: Stop all services"
  echo "  - restart.sh: Quick restart services"
  echo "  - test.sh: Test system health"
  echo "  - update.sh: Auto-update from GitHub"
}

# Show status
show_status() {
  echo
  echo "🎉 CRM/ERP System Successfully Deployed!"
  echo "========================================"
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
  echo "📁 Installation Directory: $INSTALL_DIR"
  echo "📝 Logs:"
  echo "   Backend: $INSTALL_DIR/backend/django.log"
  echo "   Frontend: $INSTALL_DIR/frontend/react.log"
  echo
  echo "🛠️ Management Commands:"
  echo "   Stop: $INSTALL_DIR/stop.sh"
  echo "   Restart: $INSTALL_DIR/restart.sh"
  echo "   Test: $INSTALL_DIR/test.sh"
  echo "   Update: $INSTALL_DIR/update.sh"
  echo
}

# Main execution
main() {
  print_step "Starting Enhanced Auto-Deploy Process..."
  
  clean_install
  clone_fresh
  setup_backend
  setup_frontend
  start_services
  create_scripts
  show_status
  
  print_success "🎉 Deployment completed successfully!"
  echo "The system is now running and ready to use!"
}

# Run main function
main "$@"