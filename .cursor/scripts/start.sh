#!/usr/bin/env bash
set -euo pipefail

if ! sudo service postgresql status >/dev/null 2>&1; then
  sudo service postgresql start
fi

if ! redis-cli ping >/dev/null 2>&1; then
  redis-server --daemonize yes
fi

echo "PostgreSQL and Redis are running"
