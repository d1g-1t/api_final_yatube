# =============================================================================
# StreamHub API - Makefile
# Удобные команды для управления проектом
# =============================================================================

.PHONY: help install build up down restart logs shell bash migrate makemigrations \
        superuser test test-cov lint format clean db-reset cache-clear backup restore \
        prod-build prod-up prod-down monitoring

# =============================================================================
# ОСНОВНЫЕ КОМАНДЫ
# =============================================================================

help: ## Показать эту справку
	@echo "📚 Доступные команды:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "💡 Быстрый старт: make install"

install: clean build up migrate superuser ## 🚀 Полная установка и запуск проекта
	@echo "✅ Проект успешно установлен!"
	@echo "📝 Создайте .env файл с вашими настройками"
	@echo "🌐 Откройте http://localhost:8000"
	@echo "📖 API документация: http://localhost:8000/api/docs/"

# =============================================================================
# DOCKER КОМАНДЫ
# =============================================================================

build: ## 🔨 Сборка Docker образов
	@echo "🔨 Сборка Docker образов..."
	docker-compose build --no-cache

up: ## 🚀 Запуск контейнеров
	@echo "🚀 Запуск контейнеров..."
	docker-compose up -d
	@echo "⏳ Ожидание готовности сервисов..."
	@sleep 10
	@echo "✅ Сервисы запущены!"
	@make ps

down: ## ⏹️ Остановка контейнеров
	@echo "⏹️  Остановка контейнеров..."
	docker-compose down

stop: down ## Алиас для down

restart: ## 🔄 Перезапуск контейнеров
	@echo "🔄 Перезапуск контейнеров..."
	docker-compose restart

ps: ## 📋 Статус контейнеров
	@docker-compose ps

logs: ## 📜 Просмотр логов (Ctrl+C для выхода)
	docker-compose logs -f --tail=100

logs-web: ## 📜 Логи web сервиса
	docker-compose logs -f web

logs-db: ## 📜 Логи базы данных
	docker-compose logs -f db

logs-redis: ## 📜 Логи Redis
	docker-compose logs -f redis

# =============================================================================
# DJANGO КОМАНДЫ
# =============================================================================

shell: ## 🐚 Django shell
	docker-compose exec web python manage.py shell

bash: ## 💻 Bash в контейнере web
	docker-compose exec web bash

migrate: ## 📦 Применение миграций
	@echo "📦 Применение миграций..."
	docker-compose exec web python manage.py migrate

makemigrations: ## 📝 Создание миграций
	@echo "📝 Создание миграций..."
	docker-compose exec web python manage.py makemigrations

superuser: ## 👤 Создание суперпользователя
	@echo "👤 Создание суперпользователя..."
	docker-compose exec web python manage.py createsuperuser

collectstatic: ## 📁 Сбор статических файлов
	docker-compose exec web python manage.py collectstatic --noinput

loaddata: ## 📥 Загрузка тестовых данных
	docker-compose exec web python manage.py loaddata fixtures/*.json

# =============================================================================
# БАЗА ДАННЫХ
# =============================================================================

db-shell: ## 🗄️  PostgreSQL shell
	docker-compose exec db psql -U streamhub_user -d streamhub_db

db-reset: ## ⚠️  ОПАСНО! Полный сброс базы данных
	@echo "⚠️  ВНИМАНИЕ! Это удалит все данные!"
	@echo "Нажмите Ctrl+C для отмены, Enter для продолжения"
	@read confirm
	docker-compose exec web python manage.py flush --noinput
	@make migrate

db-backup: ## 💾 Резервное копирование БД
	@echo "💾 Создание резервной копии..."
	@mkdir -p backups
	docker-compose exec -T db pg_dump -U streamhub_user streamhub_db > \
		backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup создан в папке backups/"

db-restore: ## 📥 Восстановление БД из backup (FILE=backup.sql)
	@echo "📥 Восстановление из $(FILE)..."
	docker-compose exec -T db psql -U streamhub_user streamhub_db < $(FILE)
	@echo "✅ База данных восстановлена"

# =============================================================================
# ТЕСТИРОВАНИЕ
# =============================================================================

test: ## 🧪 Запуск всех тестов
	@echo "🧪 Запуск тестов..."
	docker-compose exec web pytest -v

test-cov: ## 📊 Тесты с покрытием
	@echo "📊 Запуск тестов с покрытием..."
	docker-compose exec web pytest --cov=src --cov-report=html --cov-report=term

test-fast: ## ⚡ Быстрые тесты (без интеграционных)
	docker-compose exec web pytest -v -m "not slow"

test-watch: ## 👀 Тесты в режиме наблюдения
	docker-compose exec web ptw -- -v

# =============================================================================
# КАЧЕСТВО КОДА
# =============================================================================

lint: ## 🔍 Проверка кода (ruff, black, isort)
	@echo "🔍 Проверка кода..."
	docker-compose exec web ruff check src/
	docker-compose exec web black --check src/
	docker-compose exec web isort --check-only src/

format: ## ✨ Форматирование кода
	@echo "✨ Форматирование кода..."
	docker-compose exec web black src/
	docker-compose exec web isort src/
	docker-compose exec web ruff check --fix src/

type-check: ## 🔬 Проверка типов (mypy)
	docker-compose exec web mypy src/

security: ## 🔒 Проверка безопасности
	docker-compose exec web bandit -r src/
	docker-compose exec web safety check

# =============================================================================
# КЭШИРОВАНИЕ
# =============================================================================

cache-clear: ## 🗑️  Очистка кэша Redis
	@echo "🗑️  Очистка кэша..."
	docker-compose exec redis redis-cli FLUSHALL
	@echo "✅ Кэш очищен"

cache-stats: ## 📊 Статистика кэша
	docker-compose exec redis redis-cli INFO stats

# =============================================================================
# PRODUCTION
# =============================================================================

prod-build: ## 🏭 Сборка для продакшена
	@echo "🏭 Сборка production образа..."
	docker-compose --profile production build

prod-up: ## 🚀 Запуск в production режиме
	@echo "🚀 Запуск production..."
	docker-compose --profile production up -d

prod-down: ## ⏹️  Остановка production
	docker-compose --profile production down

prod-logs: ## 📜 Логи production
	docker-compose --profile production logs -f

# =============================================================================
# УТИЛИТЫ
# =============================================================================

clean: ## 🧹 Очистка временных файлов и контейнеров
	@echo "🧹 Очистка..."
	docker-compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true
	@echo "✅ Очистка завершена"

clean-all: clean ## 🧹 Полная очистка (включая volumes)
	docker system prune -af --volumes
	@echo "✅ Полная очистка завершена"

monitoring: ## 📊 Статистика использования ресурсов
	docker stats

health: ## 🏥 Проверка health контейнеров
	@echo "🏥 Проверка здоровья сервисов..."
	@docker-compose ps | grep -E "healthy|running"

update-deps: ## 📦 Обновление зависимостей
	docker-compose exec web pip install --upgrade pip
	docker-compose exec web pip list --outdated

requirements: ## 📋 Генерация requirements.txt
	docker-compose exec web pip freeze > requirements.txt

# =============================================================================
# ИНФОРМАЦИЯ
# =============================================================================

info: ## ℹ️  Информация о проекте
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
