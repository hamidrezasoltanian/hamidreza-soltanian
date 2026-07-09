# Click CRM — Agent Instructions

## Project layout

- `crm-erp-system/backend/` — Django REST API (Python 3.12+, PostgreSQL, Redis)
- `crm-erp-system/frontend/` — React + TypeScript UI (Node.js 20)
- `crm-erp-system/docker-compose.yml` — optional full-stack Docker deployment

The root-level `backend/` and `frontend/` directories are partial copies; prefer `crm-erp-system/` for development and testing.

## Cursor Cloud specific instructions

Cloud agents use `.cursor/environment.json` to provision PostgreSQL, Redis, Python, and Node.js automatically.

### Verify the environment

```bash
bash .cursor/scripts/install.sh
bash crm-erp-system/test.sh
```

### Run services manually

```bash
bash .cursor/scripts/start.sh

# Backend (port 8000)
cd crm-erp-system/backend
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Frontend (port 3000)
cd crm-erp-system/frontend
BROWSER=none PORT=3000 NODE_OPTIONS=--openssl-legacy-provider npm start
```

### Default credentials

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| Django Admin | http://localhost:8000/admin/ | admin | admin123 |
| API | http://localhost:8000/api/v1/ | — | JWT via `/api/v1/auth/login/` |
| Frontend | http://localhost:3000 | — | — |

### Common commands

```bash
# Backend tests
cd crm-erp-system/backend && source .venv/bin/activate && python manage.py test

# Frontend build (legacy OpenSSL flag may be required on newer Node versions)
cd crm-erp-system/frontend && NODE_OPTIONS=--openssl-legacy-provider npm run build

# Docker (optional)
cd crm-erp-system && docker compose up --build -d
```

### Environment variables

Copy `crm-erp-system/backend/.env.example` to `.env` for local overrides. Do not commit secrets. Use Cursor Secrets for production credentials.
