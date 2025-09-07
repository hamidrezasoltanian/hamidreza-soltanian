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
