#!/bin/bash

# Fix Login Issues Script
set -euo pipefail

echo "🔐 Fixing Login Issues for CRM/ERP System"
echo "========================================="
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

# Go to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Check if Django is running
print_status "Checking if Django is running..."
if ! curl -s http://localhost:8000/admin/ >/dev/null 2>&1; then
    print_status "Starting Django server..."
    nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
    echo $! > django.pid
    sleep 5
fi

# Create superuser
print_status "Creating admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
import django.contrib.auth.hashers as hashers

# Delete existing admin user if exists
User.objects.filter(username='admin').delete()

# Create new admin user
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)
print('Admin user created successfully!')
print('Username: admin')
print('Password: admin123')
"

# Also create a test user
print_status "Creating test user..."
python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.filter(username='test').delete()
test_user = User.objects.create_user(
    username='test',
    email='test@example.com',
    password='test123'
)
print('Test user created successfully!')
print('Username: test')
print('Password: test123')
"

# Show all users
print_status "Listing all users..."
python manage.py shell -c "
from django.contrib.auth.models import User
users = User.objects.all()
print('All users in database:')
for user in users:
    print(f'  - {user.username} ({"Superuser" if user.is_superuser else "Regular user"})')
"

print_success "🎉 Login issues fixed!"
echo "============================="
echo
echo "🔑 Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo
echo "   Username: test"
echo "   Password: test123"
echo
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Admin:    http://localhost:8000/admin"
echo
print_success "You can now login to the system!"