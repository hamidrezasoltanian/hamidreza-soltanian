#!/bin/bash

# Robust Deployment Script for CRM/ERP
# - Uses dynamic paths (relative to this script)
# - Optionally pulls latest from GitHub if repo present or REPO_URL is provided
# - Sets up backend (Django) and frontend (React)

set -euo pipefail

echo "🚀 Starting CRM/ERP System Deployment..."
echo "=========================================="
echo "🚀 CRM/ERP System Deployment Script"
echo "=========================================="
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Resolve dirs
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$SCRIPT_DIR"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Optional: provide to auto-clone if not a repo
# export REPO_URL="https://github.com/<user>/<repo>.git"
REPO_URL="${REPO_URL:-}"
BRANCH_NAME="${BRANCH_NAME:-main}"

update_code() {
  print_status "Checking repository state..."

  if [ -d "$ROOT_DIR/.git" ]; then
    print_status "Git repository detected. Pulling latest from origin/$BRANCH_NAME..."
    cd "$ROOT_DIR"
    git fetch origin | cat
    if git rev-parse --verify "origin/$BRANCH_NAME" >/dev/null 2>&1; then
      git checkout -q "$BRANCH_NAME" || git checkout -q -B "$BRANCH_NAME"
      git reset --hard "origin/$BRANCH_NAME" | cat
      git clean -fd -x | cat || true
      print_success "Updated to latest origin/$BRANCH_NAME"
    else
      print_warning "Remote branch origin/$BRANCH_NAME not found. Skipping reset."
    fi
  else
    if [ -n "$REPO_URL" ]; then
      print_status "No git repo here. Cloning $REPO_URL ..."
      parent_dir="$(dirname "$ROOT_DIR")"
      target_name="$(basename "$ROOT_DIR")"
      cd "$parent_dir"
      rm -rf "$target_name"
      git clone --branch "$BRANCH_NAME" "$REPO_URL" "$target_name" | cat
      print_success "Cloned repository to $ROOT_DIR"
    else
      print_warning "No git repo and REPO_URL not provided. Using current files."
    fi
  fi

  # Verify structure
  if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Expected directories not found. Backend: $BACKEND_DIR, Frontend: $FRONTEND_DIR"
    exit 1
  fi
}

kill_existing_processes() {
  print_status "Killing existing processes..."
  pkill -f "python manage.py runserver" || true
  pkill -f "npm start" || true
  pkill -f "react-scripts start" || true
  # Free common ports (ignore if tools not present)
  command -v fuser >/dev/null 2>&1 && fuser -k 8000/tcp 2>/dev/null || true
  command -v fuser >/dev/null 2>&1 && fuser -k 3000/tcp 2>/dev/null || true
  print_success "Existing processes killed"
}

setup_backend() {
  print_status "Setting up Backend (Django)..."
  cd "$BACKEND_DIR"

  # Python venv
  if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
  fi
  # shellcheck source=/dev/null
  source venv/bin/activate

  print_status "Installing Python dependencies..."
  pip install --upgrade pip
  pip install -r requirements.txt

  print_status "Running migrations..."
  python manage.py makemigrations
  python manage.py migrate

  print_status "Ensuring admin user exists..."
  echo "from django.contrib.auth.models import User;\n"\
       "User.objects.filter(username='admin').exists() or "\
       "User.objects.create_superuser('admin','admin@example.com','admin123')" \
       | python manage.py shell

  print_success "Backend setup completed"
}

setup_frontend() {
  print_status "Setting up Frontend (React)..."
  cd "$FRONTEND_DIR"
  if [ ! -f package.json ]; then
    print_error "package.json not found in $FRONTEND_DIR"
    exit 1
  fi
  npm install
  print_success "Frontend setup completed"
}

start_services() {
  print_status "Starting services..."

  # Start Django
  cd "$BACKEND_DIR"
  # shellcheck source=/dev/null
  source venv/bin/activate
  nohup python manage.py runserver 0.0.0.0:8000 > "$BACKEND_DIR/django.log" 2>&1 &
  echo $! > "$BACKEND_DIR/django.pid"

  sleep 5
  if curl -s http://localhost:8000/api/v1/ > /dev/null; then
    print_success "Django server is running on http://localhost:8000"
  else
    print_warning "Django server might not be ready yet"
  fi

  # Start React
  cd "$FRONTEND_DIR"
  nohup npm start > "$FRONTEND_DIR/react.log" 2>&1 &
  echo $! > "$FRONTEND_DIR/react.pid"

  sleep 8
  if curl -s http://localhost:3000 > /dev/null; then
    print_success "React server is running on http://localhost:3000"
  else
    print_warning "React server might not be ready yet"
  fi

  print_success "All services started"
}

create_util_scripts() {
  print_status "Creating helper scripts..."

  cat > "$ROOT_DIR/stop.sh" << 'EOF'
#!/bin/bash
set -e
echo "🛑 Stopping CRM/ERP System..."
BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)/backend"
FRONTEND_DIR="$(cd "$(dirname "$0")" && pwd)/frontend"

if [ -f "$BACKEND_DIR/django.pid" ]; then
  kill "$(cat "$BACKEND_DIR/django.pid")" 2>/dev/null || true
  rm -f "$BACKEND_DIR/django.pid"
  echo "✅ Django server stopped"
fi
if [ -f "$FRONTEND_DIR/react.pid" ]; then
  kill "$(cat "$FRONTEND_DIR/react.pid")" 2>/dev/null || true
  rm -f "$FRONTEND_DIR/react.pid"
  echo "✅ React server stopped"
fi
pkill -f "python manage.py runserver" || true
pkill -f "npm start" || true
pkill -f "react-scripts start" || true
echo "✅ All services stopped"
EOF
  chmod +x "$ROOT_DIR/stop.sh"

  cat > "$ROOT_DIR/quick-deploy.sh" << 'EOF'
#!/bin/bash
set -e
echo "⚡ Quick Deploy - Restarting Services..."
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

pkill -f "python manage.py runserver" || true
pkill -f "npm start" || true
pkill -f "react-scripts start" || true
sleep 2

cd "$BACKEND_DIR" && source venv/bin/activate && nohup python manage.py runserver 0.0.0.0:8000 > "$BACKEND_DIR/django.log" 2>&1 & echo $! > "$BACKEND_DIR/django.pid"
cd "$FRONTEND_DIR" && nohup npm start > "$FRONTEND_DIR/react.log" 2>&1 & echo $! > "$FRONTEND_DIR/react.pid"

echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "👤 Admin: http://localhost:8000/admin"
echo "🔑 Login: admin / admin123"
EOF
  chmod +x "$ROOT_DIR/quick-deploy.sh"

  cat > "$ROOT_DIR/test.sh" << 'EOF'
#!/bin/bash
set -e
echo "🧪 Testing CRM/ERP System..."
curl -sSf http://localhost:8000/api/v1/ >/dev/null && echo "✅ Backend OK" || echo "❌ Backend not responding"
curl -sSf http://localhost:3000 >/dev/null && echo "✅ Frontend OK" || echo "❌ Frontend not responding"
EOF
  chmod +x "$ROOT_DIR/test.sh"

  print_success "Helper scripts created: stop.sh, quick-deploy.sh, test.sh"
}

show_status() {
  echo
  echo "🌐 Frontend (React): http://localhost:3000"
  echo "🔧 Backend (Django): http://localhost:8000"
  echo "👤 Admin Panel: http://localhost:8000/admin"
  echo "📊 API Base: http://localhost:8000/api/v1/"
  echo
  echo "🔑 Login Credentials: admin / admin123"
}

# Main
kill_existing_processes
update_code
setup_backend
setup_frontend
start_services
create_util_scripts
show_status

print_success "🎉 Deployment completed successfully!"
echo "You can now access the system at http://localhost:3000"

