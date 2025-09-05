#!/bin/bash

# CRM/ERP System Docker Setup Script
# This script sets up the development environment using Docker

set -e

echo "🐳 Setting up CRM/ERP System with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles
mkdir -p reports

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec backend python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
docker-compose exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
" 2>/dev/null || echo "Superuser already exists"

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec backend python manage.py collectstatic --noinput

echo "✅ Setup completed successfully!"
echo ""
echo "🎉 Services are running:"
echo "   🌐 Web Application: http://localhost"
echo "   🔧 Admin Panel: http://localhost/admin/"
echo "   📚 API Documentation: http://localhost/api/v1/"
echo ""
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📋 Useful commands:"
echo "   docker-compose logs -f backend    # View backend logs"
echo "   docker-compose logs -f db         # View database logs"
echo "   docker-compose exec backend python manage.py shell  # Django shell"
echo "   docker-compose down               # Stop all services"
echo "   docker-compose up -d              # Start all services"