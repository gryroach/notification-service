# Запуск всех контейнеров
run-all:
	docker compose up -d --build

# Запуск api
run-api:
	docker compose up -d --build api nginx

# Запуск воркера запланированных рассылок
run-scheduler:
	docker compose up -d --build worker-scheduler

# Запуск воркера формирования и отправки сообщений с приоритетом
run-former-high:
	docker compose up -d --build worker-former-high

run-former-medium:
	docker compose up -d --build worker-former-medium

run-former-low:
	docker compose up -d --build worker-former-low

# Запуск инструмента для тестирования отправки электронной почты
run-test-sender:
	docker compose up -d --build mailhog

run-repeater:
	docker compose up -d --build worker-repeater

# Остановка и удаление всех контейнеров
down:
	docker compose down
