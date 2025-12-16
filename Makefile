.PHONY: help install restart-all setup-env build up down restart logs shell bash migrate makemigrations \
        superuser test test-cov lint format clean db-reset cache-clear backup restore \
        prod-build prod-up prod-down monitoring


help:
	@echo "📚 Доступные команды:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "💡 Первая установка: make install"
	@echo "💡 Перезапуск проекта: make restart-all"

install: clean setup-env build up
	@echo "✅ Проект успешно установлен!"
	@echo "🌐 Откройте http://localhost:8000"
	@echo "📖 API документация: http://localhost:8000/api/docs/"
	@echo "👤 Создайте суперпользователя: make superuser"

restart-all: down setup-env up
	@echo "✅ Проект перезапущен!"
	@echo "🌐 Откройте http://localhost:8000"

setup-env:
	@if [ ! -f .env ]; then \
		echo "📝 Создание .env файла из .env.example..."; \
		cp .env.example .env; \
		echo "✅ .env файл создан"; \
	else \
		echo "✅ .env файл уже существует"; \
	fi

build:
	@echo "🔨 Сборка Docker образов..."
	docker-compose build

up:
	@echo "🚀 Запуск контейнеров..."
	docker-compose up -d
	@echo "⏳ Ожидание готовности сервисов..."
	@sleep 15
	@echo "✅ Сервисы запущены!"
	@make ps

down:
	@echo "⏹️  Остановка контейнеров..."
	docker-compose down

stop: down

restart:
	@echo "🔄 Перезапуск контейнеров..."
	docker-compose restart

ps:
	@docker-compose ps

logs:
	docker-compose logs -f --tail=100

logs-web:
	docker-compose logs -f web

logs-db:
	docker-compose logs -f db

logs-redis:
	docker-compose logs -f redis

# =============================================================================
# DJANGO КОМАНДЫ
# =============================================================================

shell:
	docker-compose exec web python manage.py shell

bash:
	docker-compose exec web bash

migrate:
	@echo "📦 Применение миграций..."
	docker-compose exec web python manage.py migrate

makemigrations:
	@echo "📝 Создание миграций..."
	docker-compose exec web python manage.py makemigrations

superuser:
	@echo "👤 Создание суперпользователя..."
	docker-compose exec web python manage.py createsuperuser

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

loaddata:
	docker-compose exec web python manage.py loaddata fixtures/*.json

# =============================================================================
# БАЗА ДАННЫХ
# =============================================================================

db-shell:
	docker-compose exec db psql -U streamhub_user -d streamhub_db

db-reset:
	@echo "⚠️  ВНИМАНИЕ! Это удалит все данные!"
	@echo "Нажмите Ctrl+C для отмены, Enter для продолжения"
	@read confirm
	docker-compose exec web python manage.py flush --noinput
	@make migrate

db-backup:
	@echo "💾 Создание резервной копии..."
	@mkdir -p backups
	docker-compose exec -T db pg_dump -U streamhub_user streamhub_db > \
		backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup создан в папке backups/"

db-restore:
	@echo "📥 Восстановление из $(FILE)..."
	docker-compose exec -T db psql -U streamhub_user streamhub_db < $(FILE)
	@echo "✅ База данных восстановлена"

# =============================================================================
# ТЕСТИРОВАНИЕ
# =============================================================================

test:
	@echo "🧪 Запуск тестов..."
	docker-compose exec web pytest -v

test-cov:
	@echo "📊 Запуск тестов с покрытием..."
	docker-compose exec web pytest --cov=src --cov-report=html --cov-report=term

test-fast:
	docker-compose exec web pytest -v -m "not slow"

test-watch:
	docker-compose exec web ptw -- -v

# =============================================================================
# КАЧЕСТВО КОДА
# =============================================================================

lint:
	@echo "🔍 Проверка кода..."
	docker-compose exec web ruff check src/
	docker-compose exec web black --check src/
	docker-compose exec web isort --check-only src/

format:
	@echo "✨ Форматирование кода..."
	docker-compose exec web black src/
	docker-compose exec web isort src/
	docker-compose exec web ruff check --fix src/

type-check:
	docker-compose exec web mypy src/

security:
	docker-compose exec web bandit -r src/
	docker-compose exec web safety check

# =============================================================================
# КЭШИРОВАНИЕ
# =============================================================================

cache-clear:
	@echo "🗑️  Очистка кэша..."
	docker-compose exec redis redis-cli FLUSHALL
	@echo "✅ Кэш очищен"

cache-stats:
	docker-compose exec redis redis-cli INFO stats

# =============================================================================
# PRODUCTION
# =============================================================================

prod-build:
	@echo "🏭 Сборка production образа..."
	docker-compose --profile production build

prod-up:
	@echo "🚀 Запуск production..."
	docker-compose --profile production up -d

prod-down:
	docker-compose --profile production down

prod-logs:
	docker-compose --profile production logs -f

# =============================================================================
# УТИЛИТЫ
# =============================================================================

clean:
	@echo "🧹 Очистка..."
	docker-compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true
	@echo "✅ Очистка завершена"

clean-all: clean
	docker system prune -af --volumes
	@echo "✅ Полная очистка завершена"

monitoring:
	docker stats

health:
	@echo "🏥 Проверка здоровья сервисов..."
	@docker-compose ps | grep -E "healthy|running"

update-deps:
	docker-compose exec web pip install --upgrade pip
	docker-compose exec web pip list --outdated

requirements:
	docker-compose exec web pip freeze > requirements.txt

# =============================================================================
# ИНФОРМАЦИЯ
# =============================================================================

info:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🚀 StreamHub API"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "📍 URL: http://localhost:8000"
	@echo "📖 API Docs: http://localhost:8000/api/docs/"
	@echo "👤 Admin: http://localhost:8000/admin/"
	@echo "🗄️  Database: PostgreSQL 16"
	@echo "💾 Cache: Redis 7"
	@echo "🐍 Python: 3.12"
	@echo "🎯 Django: 5.0"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

.DEFAULT_GOAL := help
