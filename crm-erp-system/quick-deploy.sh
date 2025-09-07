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
