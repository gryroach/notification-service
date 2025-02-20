#!/usr/bin/env bash

# Применяем миграции
uv run alembic upgrade head

# Запуск тестов
uv run pytest -v --asyncio-mode=auto ./src/tests
