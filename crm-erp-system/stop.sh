#!/bin/bash
echo "🛑 Stopping CRM/ERP System..."
pkill -f "python manage.py runserver" || true
pkill -f "npm start" || true
pkill -f "react-scripts start" || true
echo "✅ All services stopped"
