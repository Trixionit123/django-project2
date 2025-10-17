#!/usr/bin/env sh
set -e

# Wait for DB if provided
if [ -n "$DB_HOST" ]; then
  echo "Waiting for DB at $DB_HOST:$DB_PORT..."
  for i in $(seq 1 60); do
    nc -z "$DB_HOST" "${DB_PORT:-5432}" && break
    sleep 1
  done
fi

python manage.py migrate --noinput

case "$1" in
  web)
    exec python manage.py runserver 0.0.0.0:8000
    ;;
  worker)
    exec python -m celery -A myproject worker -l info
    ;;
  beat)
    exec python -m celery -A myproject beat -l info
    ;;
  *)
    exec "$@"
    ;;
esac




