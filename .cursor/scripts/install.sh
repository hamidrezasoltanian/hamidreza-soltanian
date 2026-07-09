#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
APP_DIR="${ROOT_DIR}/crm-erp-system"
BACKEND_DIR="${APP_DIR}/backend"
FRONTEND_DIR="${APP_DIR}/frontend"
VENV_DIR="${BACKEND_DIR}/.venv"

echo "==> Installing Click CRM development dependencies"

if [ ! -d "${APP_DIR}" ]; then
  echo "Expected application directory at ${APP_DIR}" >&2
  exit 1
fi

# PostgreSQL
if ! sudo service postgresql status >/dev/null 2>&1; then
  sudo service postgresql start
fi

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='postgres'" | grep -q 1 \
  || sudo -u postgres createuser --superuser postgres 2>/dev/null || true

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='crm_erp'" | grep -q 1 \
  || sudo -u postgres createdb crm_erp

# Redis
if ! redis-cli ping >/dev/null 2>&1; then
  redis-server --daemonize yes
fi

# Backend
cd "${BACKEND_DIR}"

if [ ! -f .env ]; then
  cp .env.example .env
fi

# Keep PostgreSQL credentials aligned with backend .env for local/cloud dev
DB_PASSWORD="$(grep -E '^DB_PASSWORD=' .env | head -1 | cut -d= -f2- | tr -d "'\" ")"
DB_PASSWORD="${DB_PASSWORD:-password}"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '${DB_PASSWORD}';" >/dev/null

if [ ! -d "${VENV_DIR}" ]; then
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

mkdir -p logs media staticfiles reports

python manage.py migrate --noinput

python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
" >/dev/null 2>&1 || true

python manage.py collectstatic --noinput >/dev/null 2>&1 || true

# Frontend
cd "${FRONTEND_DIR}"
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

echo "==> Click CRM development environment is ready"
