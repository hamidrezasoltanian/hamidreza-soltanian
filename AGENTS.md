# AGENTS.md

## Cursor Cloud specific instructions

### What runs
The runnable product lives entirely in **`crm-erp-system/`**: a Django REST API
backend (`crm-erp-system/backend`) and a Create-React-App frontend
(`crm-erp-system/frontend`), backed by PostgreSQL and Redis.

The top-level `backend/` and `frontend/` directories are **incomplete feature
stubs** (no `manage.py`, no React entry point) and are not runnable on their own —
ignore them for running/testing the app.

### Required services (start these first)
PostgreSQL and Redis are installed but do **not** auto-start (no systemd in this
container). Start them before running the backend:

```bash
sudo pg_ctlcluster 16 main start
sudo redis-server /etc/redis/redis.conf --daemonize yes
```

Redis is not optional: sessions, cache, and login rate-limiting are all
Redis-backed, so **login and most API calls 500 if Redis is down**.

The `crm_erp` Postgres database and the `postgres` user password (`62604193`,
matching `crm-erp-system/backend/.env`) persist in the VM snapshot. If the DB is
ever empty, recreate it and re-run:
```bash
sudo -u postgres createdb crm_erp
cd crm-erp-system/backend && ./venv/bin/python manage.py migrate
```
Admin user is `admin` / `admin123` (create via `createsuperuser` if missing).

### Run the backend (dev)
```bash
cd crm-erp-system/backend
./venv/bin/python manage.py runserver 0.0.0.0:8000
```
API base `http://localhost:8000/api/v1/`, admin at `/admin/`. The venv lives at
`crm-erp-system/backend/venv` (created by the update script).

### Run the frontend (dev)
```bash
cd crm-erp-system/frontend
TSC_COMPILE_ON_ERROR=true ESLINT_NO_DEV_ERRORS=true BROWSER=none npm start
```
Serves on `http://localhost:3000` and proxies API calls to `:8000`.

`TSC_COMPILE_ON_ERROR=true` is **required**: the app source has pre-existing
TypeScript type mismatches (code targets `@tanstack/react-query` v4 while v5 is
installed — e.g. `cacheTime`, error typing). Babel transpiles them fine, so they
are runtime-safe warnings, but without this flag CRA treats them as fatal.

### Tests
Test dependencies (`pytest`, `pytest-django`, `pytest-cov`, `factory_boy`,
`faker`) are not in `requirements.txt`; the update script installs them.
Only `customers/tests.py` contains real tests (the other apps' `tests.py` are
empty stubs), and it currently has a pre-existing import bug (`CustomerPersonnel`
is not defined in `customers/models.py`), so it fails to collect — this is a repo
code issue, not an environment one. Note `pytest.ini` uses a `[tool:pytest]`
header, which pytest ignores in a `.ini` file, so run modules explicitly with
`-o python_files=tests.py` and `DJANGO_SETTINGS_MODULE=crm_erp.settings`.

### Lint
There is no backend linter in the project dependencies (CI uses
`flake8`/`black`/`isort`, installed ad-hoc). Frontend linting runs automatically
via `react-scripts` (ESLint `react-app` config) during `npm start`/`npm run build`.
