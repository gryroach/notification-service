# Запуск всех контейнеров
run-all:
	docker compose up -d --build

# Запуск api
run-api:
	docker compose up -d --build api nginx

# Запуск воркера запланированных рассылок
run-scheduler:
	docker compose up -d --build worker-scheduler

# Остановка и удаление всех контейнеров
down:
	docker compose down
