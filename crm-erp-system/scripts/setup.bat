@echo off
REM CRM/ERP System Setup Script for Windows
REM This script sets up the development environment

echo 🚀 Setting up CRM/ERP System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.13+ first.
    pause
    exit /b 1
)

REM Check if PostgreSQL is installed
psql --version >nul 2>&1
if errorlevel 1 (
    echo ❌ PostgreSQL is not installed. Please install PostgreSQL 17+ first.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Navigate to backend directory
cd backend

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    copy .env.example .env
)

REM Create database (assuming PostgreSQL is running)
echo 🗄️ Creating database...
psql -U postgres -c "CREATE DATABASE crm_erp;" 2>nul || echo Database already exists
psql -U postgres -c "ALTER USER postgres PASSWORD 'password';" 2>nul || echo Password already set

REM Run migrations
echo 🔄 Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Create superuser
echo 👤 Creating superuser...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') | python manage.py shell 2>nul || echo Superuser already exists

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

echo ✅ Setup completed successfully!
echo.
echo 🎉 You can now start the development server:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python manage.py runserver
echo.
echo 🌐 Admin panel: http://localhost:8000/admin/
echo    Username: admin
echo    Password: admin123
echo.
echo 📚 API Documentation: http://localhost:8000/api/v1/
pause