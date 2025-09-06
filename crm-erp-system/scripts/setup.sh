#!/bin/bash

# CRM/ERP System Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up CRM/ERP System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.13+ first."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL 17+ first."
    exit 1
fi

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed. Please install Redis 6+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Navigate to backend directory
cd backend

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Start PostgreSQL service
echo "🗄️ Starting PostgreSQL..."
sudo service postgresql start

# Create database
echo "🗄️ Creating database..."
sudo -u postgres createdb crm_erp 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';" 2>/dev/null || echo "Password already set"

# Run migrations
echo "🔄 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell 2>/dev/null || echo "Superuser already exists"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start Redis
echo "🔴 Starting Redis..."
redis-server --daemonize yes

echo "✅ Setup completed successfully!"
echo ""
echo "🎉 You can now start the development server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "🌐 Admin panel: http://localhost:8000/admin/"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📚 API Documentation: http://localhost:8000/api/v1/"