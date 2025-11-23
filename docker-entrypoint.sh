#!/bin/bash
set -e

echo "🚀 Starting StreamHub API..."

# Ожидание доступности PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "✅ PostgreSQL is ready!"

# Ожидание доступности Redis
echo "⏳ Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
  sleep 0.5
done
echo "✅ Redis is ready!"

# Применение миграций
echo "📦 Applying database migrations..."
python manage.py migrate --noinput

# Сбор статических файлов
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Создание кэш-таблиц
echo "🗄️  Creating cache tables..."
python manage.py createcachetable || true

echo "✅ Initialization complete!"

# Запуск переданной команды
exec "$@"
