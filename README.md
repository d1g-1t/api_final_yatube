# StreamHub API 🚀

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.15-orange?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white)

> Еще одна соцсеть? Нет, это API для соцсети, которая не тормозит 😎

Делал этот проект, чтобы попрактиковаться в правильной архитектуре Django-приложений. Устал от легаси кода с views на 500 строк и N+1 запросами? Я тоже. Поэтому тут всё по уму.

---

## Что внутри?

### Архитектура (без боли)

- ✅ **Service Layer** - вся бизнес-логика в отдельных классах, а не размазана по views
- ✅ **Selectors** - запросы к БД живут отдельно, с кэшированием из коробки
- ✅ **Custom QuerySets** - переиспользуем код, а не копипастим
- ✅ **Soft Delete** - "удалённые" данные на самом деле просто скрыты (всякое бывает)

### Производительность (главное)

- 🚀 **Redis кэширование** - потому что запрашивать БД каждый раз - это прошлый век
- 🚀 **Оптимизация запросов** - `select_related`, `prefetch_related` везде где надо (прощай N+1)
- 🚀 **Индексы в БД** - потому что EXPLAIN ANALYZE должен радовать глаз
- 🚀 **Connection pooling** - переиспользуем соединения с Postgres

### Безопасность (потому что надо)

- 🔐 **JWT токены** - храним состояние на клиенте, сервер ничего не помнит
- 🔐 **Permissions** - каждый endpoint проверяет права
- 🔐 **Валидация** - Django validators ловят косяки на входе
- 🔐 **CORS** - фронтенд с другого домена? Не проблема

### Для удобства

- 📖 **Swagger UI** - документация API, которую не стыдно показать фронтендерам
- 📖 **Type hints** - потому что угадывать типы в 2025 году не модно
- 🐳 **Docker** - `make install` и всё работает (ну почти)
- 🐳 **Makefile** - команды для всего, от миграций до бэкапов

---

## 📁 Структура проекта

```
streamhub/
├── streamhub/                    # Исходный код приложения
│   ├── config/                  # Конфигурация Django
│   │   ├── settings/           # Настройки для разных окружений
│   │   │   ├── base.py        # Базовые настройки
│   │   │   ├── development.py # Настройки для разработки
│   │   │   └── production.py  # Продакшен настройки
│   │   ├── urls.py            # Главный роутинг
│   │   ├── wsgi.py            # WSGI приложение
│   │   └── asgi.py            # ASGI приложение
│   ├── common/                  # Общие компоненты
│   │   ├── models.py          # Абстрактные базовые модели
│   │   ├── cache.py           # Утилиты кэширования
│   │   ├── pagination.py      # Кастомная пагинация
│   │   ├── permissions.py     # Расширенные права доступа
│   │   └── exceptions.py      # Обработка ошибок
│   ├── apps/                    # Django приложения
│   │   ├── posts/              # Посты и сообщества
│   │   │   ├── models.py      # Модели (Post, Community)
│   │   │   ├── services.py    # Бизнес-логика
│   │   │   ├── selectors.py   # Оптимизированные запросы
│   │   │   ├── serializers.py # DRF сериализаторы
│   │   │   └── views.py       # API endpoints
│   │   ├── interactions/       # Взаимодействия
│   │   │   └── models.py      # Comment, Subscription, Like
│   │   ├── communities/        # Управление сообществами
│   │   └── users/             # Управление пользователями
│   ├── manage.py               # Django management
│   ├── media/                  # Загруженные файлы
│   └── staticfiles/           # Статические файлы
├── tests/                        # Тесты
├── Dockerfile                    # Docker образ
├── docker-compose.yml            # Оркестрация сервисов
├── Makefile                      # Команды управления
├── requirements.txt              # Python зависимости
└── README.md                     # Документация
```

---

## Быстрый старт

Нужен только Docker. Всё остальное само подтянется.

### Первая установка после клонирования

```bash
git clone https://github.com/d1g-1t/streamhub-api.git
cd streamhub-api
make install
```

Эта команда:
- Очистит старые данные (если есть)
- Создаст .env файл из .env.example
- Соберёт Docker образы
- Запустит контейнеры (Postgres, Redis, Django)
- Автоматически создаст все миграции
- Применит миграции к базе данных
- Соберёт статические файлы

### Перезапуск проекта (без полной очистки)

```bash
make restart-all
```

Используйте эту команду для повторных запусков проекта без удаления volumes.

Теперь создайте админа:
```bash
make superuser
```

И можно работать:
- 🌐 API: http://localhost:8000
- 📖 Swagger (документация): http://localhost:8000/api/docs/
- 👤 Админка: http://localhost:8000/admin/

### Если хочешь настроить

Скопируй `.env.example` в `.env` и поправь что нужно:

```env
# БД
POSTGRES_DB=streamhub_db
POSTGRES_USER=streamhub_user
POSTGRES_PASSWORD=меняй_меня_в_продакшене

# Приложение
DEBUG=True  # False в продакшене!
SECRET_KEY=какой-то-рандомный-ключ
```

Но по дефолту всё работает и так

---

## Команды (всё через make)

Набери `make help` чтобы увидеть все команды. Самые нужные:

```bash
# Базовые
make up            # Поднять контейнеры
make down          # Остановить всё
make logs          # Смотреть что происходит
make restart       # Ctrl+Alt+Del для Docker

# Django штуки
make shell         # Django shell (когда нужно что-то проверить)
make bash          # Зайти в контейнер
make migrate       # Накатить миграции
make superuser     # Создать админа

# БД
make db-shell      # Postgres консоль (для SQL вручную)
make db-backup     # Бэкап на всякий случай
make db-reset      # Удалить всё и начать заново (осторожно!)

# Тесты
make test          # Прогнать тесты
make test-cov      # С покрытием кода

# Когда Redis забит
make cache-clear   # Очистить весь кэш
```

---

## 🔌 API Endpoints

### 📝 Посты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/v1/posts/` | Список всех постов |
| `POST` | `/api/v1/posts/` | Создать пост |
| `GET` | `/api/v1/posts/{id}/` | Детали поста |
| `PUT` | `/api/v1/posts/{id}/` | Обновить пост |
| `DELETE` | `/api/v1/posts/{id}/` | Удалить пост |
| `GET` | `/api/v1/posts/my_posts/` | Мои посты |
| `GET` | `/api/v1/posts/trending/` | Трендовые посты |
| `GET` | `/api/v1/posts/search/?q=query` | Поиск постов |

### 👥 Сообщества

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/v1/communities/` | Список сообществ |
| `POST` | `/api/v1/communities/` | Создать сообщество |
| `GET` | `/api/v1/communities/{slug}/` | Детали сообщества |
| `GET` | `/api/v1/communities/{slug}/posts/` | Посты сообщества |
| `GET` | `/api/v1/communities/popular/` | Популярные сообщества |

### 💬 Взаимодействия

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/v1/posts/{id}/comments/` | Комментарии поста |
| `POST` | `/api/v1/posts/{id}/comments/` | Добавить комментарий |
| `POST` | `/api/v1/posts/{id}/like/` | Лайкнуть пост |
| `GET` | `/api/v1/subscriptions/` | Мои подписки |
| `POST` | `/api/v1/subscriptions/` | Подписаться на пользователя |

### 🔐 Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/v1/auth/jwt/create/` | Получить JWT токен |
| `POST` | `/api/v1/auth/jwt/refresh/` | Обновить токен |
| `POST` | `/api/v1/auth/jwt/verify/` | Проверить токен |
| `POST` | `/api/v1/auth/users/` | Регистрация |

---

## Технологии

Стандартный стек для 2025 года:

**Backend:**
- Django 5.0 + DRF 3.15 (классика)
- PostgreSQL 16 (потому что MySQL это боль)
- Redis 7 (для кэша, что ещё)
- Gunicorn (production сервер)

**Аутентификация:**
- JWT токены через simplejwt
- Djoser для регистрации/авторизации

**Для удобства разработки:**
- drf-spectacular (Swagger генератор, живая документация)
- django-filter (фильтры в API)
- Pillow (картинки)

**DevOps:**
- Docker + docker-compose (локально работает == в продакшене работает)
- Makefile (чтобы не запоминать длинные команды)

---

## Как это устроено

### Service Layer (бизнес-логика отдельно)

Views только принимают запросы и отдают ответы. Вся логика в сервисах:

```python
# services.py
class PostService:
    @staticmethod
    @transaction.atomic
    def create_post(author: User, title: str, content: str) -> Post:
        # Валидация
        if len(title) < 5:
            raise ValidationError("Заголовок слишком короткий")
        
        # Создаём пост
        post = Post.objects.create(author=author, title=title, content=content)
        
        # Сбрасываем кэш (иначе новый пост не появится в списке)
        invalidate_cache_pattern('post_list')
        
        return post
```

Теперь эту логику можно переиспользовать где угодно - в API, в команде, в Celery таске.

### Selectors (запросы к БД)

Все запросы в отдельных классах, с кэшированием:

```python
# selectors.py
class PostSelector:
    @staticmethod
    @cache_result(timeout=300)  # 5 минут в кэше
    def get_published_posts() -> QuerySet[Post]:
        return (
            Post.objects
            .published()
            .select_related('author', 'community')  # JOIN в одном запросе
            .prefetch_related('comments__author')   # Ещё один JOIN
            .annotate(comments_count=Count('comments'))  # Считаем в БД
        )
```

Результат - вместо 50 запросов к БД делается 3. Django ORM умеет в оптимизацию, надо только правильно его попросить.

### Custom QuerySets (переиспользуем логику)

```python
# models.py
class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, is_deleted=False)
    
    def trending(self, days=7):
        date_from = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=date_from).order_by('-views_count')
```

Теперь можно делать `Post.objects.published().trending()` и это читается как обычный код

---

## Производительность

### БД не тормозит

- Индексы на всех полях которые используются в WHERE и JOIN
- Composite индексы для сложных запросов (типа `created_at + author_id`)
- Connection pooling - держим соединения открытыми, не создаём заново каждый раз

### Кэширование (главное оружие)

- Redis кэширует всё что можно - списки постов, профили, счётчики
- Инвалидация кэша автоматическая - создал пост, кэш списка сбросился сам
- Типичный запрос: 50ms из кэша vs 500ms из БД

### Можно масштабировать

- Stateless архитектура - можно поднять 10 инстансов Django, они не конфликтуют
- Docker контейнеры - добавить мощности = запустить ещё контейнер
- Готово к Celery - тяжёлые задачи выносятся в фон

---

## 🚀 Deployment

### Development

```bash
make install
```

### Production

```bash
# 1. Настройте production переменные в .env
# 2. Соберите production образы
make prod-build

# 3. Запустите с Nginx и Celery
make prod-up

# 4. Проверьте здоровье сервисов
make health
```

### Environment Variables (Production)

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_SETTINGS_MODULE=config.settings.production

POSTGRES_DB=streamhub_production
POSTGRES_USER=streamhub_prod
POSTGRES_PASSWORD=super-strong-password

# Email настройки
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🧪 Тестирование

```bash
# Все тесты
make test

# С покрытием кода
make test-cov

# Быстрые тесты (без медленных интеграционных)
make test-fast

# Тесты в режиме наблюдения
make test-watch
```

Проект поддерживает покрытие кода **>80%**.

---

## 📚 API Документация

### Swagger UI

Интерактивная документация доступна по адресу:
- Development: http://localhost:8000/api/docs/
- Production: https://your-domain.com/api/docs/

### OpenAPI Schema

JSON схема: http://localhost:8000/api/schema/

---

## Хочешь что-то добавить?

Форкай, пиши код, делай PR. Стандартная схема.

Только:
- Прогони `make test` перед коммитом (тесты должны проходить)
- Используй type hints (чтобы PyCharm не ругался)
- Пиши docstrings хотя бы для публичных методов

Код-стайл:
- PEP 8 (если не знаешь что это - гугли)
- Black для форматирования (запускается автоматом)
- Type hints везде где можно

```bash
make lint    # Проверить код
make test    # Прогнать тесты
```

Если всё зелёное - PR принимается

---

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

---

## 👤 Автор

**Pavel Okhrim**

- GitHub: [@d1g-1t](https://github.com/d1g-1t)
- Email: your.email@example.com

---

## ⭐ Поддержка

Если проект вам понравился, поставьте звезду ⭐️

---

## Что дальше?

План на будущее (если будет время и желание):

- [ ] WebSockets для уведомлений в реальном времени
- [ ] GraphQL (REST хорош, но иногда нужна гибкость)
- [ ] Elasticsearch (полнотекстовый поиск на Postgres это не то)
- [ ] Celery (для отправки email, обработки картинок и т.д.)
- [ ] S3 для файлов (локальное хранение это для разработки)
- [ ] CI/CD через GitHub Actions (автотесты на каждый PR)
- [ ] Мониторинг (Prometheus + Grafana, чтобы видеть что происходит)
- [ ] Rate limiting (чтобы API не положили спамом)

---

## Автор

Делал этот проект чтобы попрактиковаться в правильной архитектуре Django.
Если нашёл баг или есть идеи - пиши в issues.

**Pavel Okhrim** / [@d1g-1t](https://github.com/d1g-1t)

---

*P.S. Если проект помог - поставь звезду ⭐, мне будет приятно*

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![DRF](https://img.shields.io/badge/DRF-3.15-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

Современный высокопроизводительный RESTful API для социальной платформы, построенный с использованием лучших практик разработки на Django REST Framework.

## 🚀 О проекте

StreamHub API - это современное решение для создания социальных платформ с акцентом на производительность и масштабируемость. Проект демонстрирует применение лучших практик backend-разработки.

## ⭐ Особенности

✅ **Service Layer Pattern** - четкое разделение бизнес-логики и представления
✅ **Selector Pattern** - оптимизированные запросы к БД с кэшированием
✅ **Redis кэширование** - многоуровневое кэширование для максимальной производительности
✅ **Docker контейнеризация** - полная изоляция окружения
✅ **PostgreSQL** - надежное хранение с оптимизированными индексами
✅ **JWT Authentication** - безопасная аутентификация без состояния
✅ **Swagger/OpenAPI** - автодокументация API
✅ **Оптимизация запросов** - select_related, prefetch_related, аннотации
✅ **Структурированное логирование** - детальное отслеживание операций
✅ **UV Package Manager** - молниеносная установка зависимостей

## 📁 Архитектура

```
streamhub/
├── streamhub/              # Исходный код
│   ├── config/            # Конфигурация Django
│   ├── common/            # Общие компоненты
│   │   ├── cache.py      # Утилиты кэширования
│   │   ├── pagination.py # Кастомная пагинация
│   │   └── permissions.py # Расширенные права доступа
│   └── apps/
│       ├── posts/         # Посты и сообщества
│       │   ├── models.py
│       │   ├── services.py    # Бизнес-логика
│       │   ├── selectors.py   # Оптимизированные запросы
│       │   └── views.py
│       ├── interactions/  # Комментарии и подписки
│       └── users/        # Управление пользователями
├── docker-compose.yml
├── Dockerfile
├── Makefile             # Команды управления
└── requirements.txt     # Зависимости проекта
```

## ⚡ Быстрый старт

### Установка за 2 минуты

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/d1g-1t/streamhub-api.git
cd streamhub-api
```

2. **Запустите установку**
```bash
make install
```

3. **Создайте администратора**
```bash
make superuser
```

Готово! API доступен по адресу http://localhost:8000

## 📝 Основные команды

```bash
make help         # Список всех команд
make up          # Запуск сервисов
make down        # Остановка
make logs        # Просмотр логов
make test        # Тестирование
make shell       # Django shell
```

## 🔌 API Endpoints

### Посты
- `GET /api/v1/posts/` - Список постов
- `POST /api/v1/posts/` - Создание поста
- `GET /api/v1/posts/{id}/` - Детали поста
- `GET /api/v1/posts/my_posts/` - Посты пользователя
- `GET /api/v1/posts/search/?q=query` - Поиск

### Сообщества
- `GET /api/v1/communities/` - Список сообществ
- `POST /api/v1/communities/` - Создание сообщества
- `GET /api/v1/communities/{slug}/` - Детали сообщества
- `GET /api/v1/communities/{slug}/posts/` - Посты сообщества

### Взаимодействия
- `GET /api/v1/posts/{id}/comments/` - Комментарии
- `POST /api/v1/posts/{id}/comments/` - Добавить комментарий
- `GET /api/v1/subscriptions/` - Подписки
- `POST /api/v1/subscriptions/` - Подписаться

### Документация
- `/api/docs/` - Swagger UI
- `/api/schema/` - OpenAPI схема

## 🛠 Технологии

- **Backend**: Django 5.0, DRF 3.15
- **База данных**: PostgreSQL 16 с оптимизированными индексами
- **Кэш**: Redis 7
- **Аутентификация**: JWT (simplejwt)
- **Документация**: drf-spectacular
- **Контейнеризация**: Docker, Docker Compose
- **Менеджер пакетов**: UV

## ⚡ Производительность

- Кэширование часто запрашиваемых данных
- Оптимизированные SQL запросы с индексами
- Пагинация для больших выборок
- Асинхронная обработка тяжелых операций
- Сжатие ответов API

## 💻 Разработка

### Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Миграции
python streamhub/manage.py migrate

# Запуск сервера
python streamhub/manage.py runserver
```

### Тестирование

```bash
make test         # Все тесты
make test-cov    # С покрытием
```

## 📄 Лицензия

MIT License

## 👤 Автор

**Pavel Okhrim**

- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- Email: your.email@example.com

## 🤝 Вклад в проект

Contributions, issues и feature requests приветствуются!

## ⭐ Поддержка

Если проект вам понравился, поставьте звезду ⭐️

---

**StreamHub API** - производительное решение для создания социальных платформ.

