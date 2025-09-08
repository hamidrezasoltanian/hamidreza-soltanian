# CRM/ERP System

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 17+

### Database Setup
```bash
# Set PostgreSQL password
sudo -u postgres psql -c "ALTER USER postgres PASSWORD '62604193';"

# Create database
sudo -u postgres createdb crm_erp
```

### Installation
```bash
# Clone repository
git clone https://github.com/hamidrezasoltanian/hamidreza-soltanian.git
cd hamidreza-soltanian/crm-erp-system

# Deploy system
./deploy.sh
```

### Access
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/v1/

### Login
- **Username**: admin
- **Password**: admin123

## 📋 Features

### CRM Features
- Customer Management
- Personnel Management
- Kanban CRM
- Multi-stage Invoice Approval
- Multiple Print Models

### ERP Features
- Inventory Management
- Product Catalog (Tree Structure)
- Lot Numbers & Expiry Dates
- Warehouse Receipts

### Additional Features
- Accounting System
- Tax System (Iranian Standards)
- Reporting System
- Export/Import
- Notifications
- Dark Mode

## 🛠️ Scripts

- `./deploy.sh` - Full deployment
- `./quick-deploy.sh` - Quick restart
- `./stop.sh` - Stop services
- `./test.sh` - Test system
- `./push.sh` - Push to GitHub

## 📊 Database Configuration

Update `backend/.env`:
```env
DB_NAME=crm_erp
DB_USER=postgres
DB_PASSWORD=62604193
DB_HOST=localhost
DB_PORT=5432
```

## 🔧 Development

### Backend (Django)
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### Frontend (React)
```bash
cd frontend
npm start
```

## 📝 License

MIT License