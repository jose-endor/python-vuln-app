#!/bin/sh
# RESEARCH: wait for Postgres (compose healthcheck is primary; this is extra resilience)
set -e
if [ -n "${DATABASE_URL}" ] || [ -n "${INVENTORY_DSN}" ]; then
  i=0
  until python -c "
import os, sys
u = (os.environ.get('DATABASE_URL') or os.environ.get('INVENTORY_DSN') or '').strip()
if not u:
  sys.exit(0)
import psycopg2
c = psycopg2.connect(u)
c.close()
" 2>/dev/null; do
  i=$((i+1))
  if [ "$i" -gt 90 ]; then
    echo "could not connect to database DSN" >&2
    exit 1
  fi
  echo "waiting for postgres... ($i)"
  sleep 1
done
fi
exec "$@"
