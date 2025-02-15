# Проектная работа 10 спринта

## Миграции

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