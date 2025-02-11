# Сервис Уведомлений

Микросервис для управления периодическими и запланированными уведомлениями с использованием FastAPI, PostgreSQL и Redis.

## 📦 Основные технологии

- **Python 3.12** с асинхронной обработкой
- **FastAPI** для веб-интерфейса (API)
- **PostgreSQL** + **SQLAlchemy 2.0** для хранения данных
- **RabbitMQ** для контроля нагрузки
- **Redis** для кеширования и управления состоянием
- **Alembic** для миграций баз данных
- **Sentry** для мониторинга ошибок
- **Docker** и **Nginx** для контейнеризации

## 🚀 Быстрый старт

### Требования

- Docker 20.10+
- Docker Compose 2.20+

1. Клонировать репозиторий

```
git clone https://github.com/your-repo/notifications-service.git
cd notifications-service
```

2. Создать .env файл (пример в configs/.env.example)

```
cp configs/.env.example .env
```

3. Запустить сервисы

```
docker-compose up --build
```

## ⚙️ Конфигурация

Основные настройки в `.env`.example

## 📚 API Документация

После запуска сервиса документация доступна по адресам:

- Swagger UI: `http://localhost/api-notify/openapi`
- JSON Schema: `http://localhost/api-notify/openapi.json`

## 🛠️ Разработка

### Установка зависимостей

```
uv pip install -r requirements.txt
```

### Запуск линтеров

```
bash
ruff check .
mypy .
isort .
```

### Работа с миграциями

Создать новую миграцию

```
uv run alembic revision --autogenerate -m "description"
```

Применить миграции

```
uv run alembic upgrade head
```

## 🔒 Безопасность

- JWT аутентификация с RSA-ключами
- Валидация входящих запросов через Pydantic
- Интеграция с Sentry для отслеживания ошибок
