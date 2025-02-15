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

Основные настройки в `.env`

## 📚 API Документация

После запуска сервиса документация доступна по адресам:

- Swagger UI: `http://localhost/api-notify/openapi`
- JSON Schema: `http://localhost/api-notify/openapi.json`

Для выполнения некоторых запросов необходимо быть авторизованным пользователем.
Для генерации access-токена можно использовать python-скрипт:

```bash
python tools/generate_token.py
```

## 🛠️ Разработка

### Установка зависимостей

Для создания виртуального окружения и установки зависимостей выполните команду:

```bash
uv sync
```

### Pre-commit хуки

Для установки pre-commit хуков выполните:

```bash
pip install pre-commit
pre-commit install
```

Это установит автоматические проверки кода перед каждым коммитом, включая:
- Проверку форматирования (trailing whitespace, end of file)
- Проверку синтаксиса YAML
- Проверку конфликтов слияния
- Сортировку импортов с помощью isort
- Форматирование и линтинг с помощью ruff
- Проверку типов с помощью mypy

### Работа с миграциями

Для создания миграций перейдите в директорию notification_service:
```bash
cd notification_service/ 
```

Пропишите PYTHONPATH:
```bash
export PYTHONPATH=./src
```

Создание миграции:
```bash
alembic revision --autogenerate -m "002_your_name"
```

Важно не забывать про нумерацию миграций для простоты отслеживания изменений.

Применение миграций:
```bash
alembic upgrade head
```
Если запуск проекта происходит в докере, то может быть проблема с подключением к БД. 
Чтобы ее решить, необходимо поменять переменные окружения `NOTIFY_POSTGRES_HOST` и
`NOTIFY_POSTGRES_PORT` на `localhost` и соответствующий порт.

## 🔒 Безопасность

- JWT аутентификация с RSA-ключами
- Валидация входящих запросов через Pydantic
- Интеграция с Sentry для отслеживания ошибок
