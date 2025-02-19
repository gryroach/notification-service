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
 
run-test-sender:
	docker compose up -d --build mailhog

run-repeater:
    docker compose up -d --build worker-repeater

# Запуск инструмента для тестирования отправки электронной почты
run-mailhog:
	docker compose up -d --build mailhog

# Запуск тестов
run-tests:
	docker compose -f docker-compose.test.yml build api-test
	docker compose -f docker-compose.test.yml up -d db redis rabbitmq api nginx --build --force-recreate
	@echo "Ожидание поднятия тестовой API..."
	@while ! curl -s http://localhost/api-notify/openapi > /dev/null; do sleep 1; done
	sleep 10
	@echo "Тестовый API успешно поднят!"
	docker compose -f docker-compose.test.yml run -T --rm api-test
	docker compose down -v

run-test-sender:
	docker compose up -d --build mailhog

run-repeater:
    docker compose up -d --build worker-repeater

# Остановка и удаление всех контейнеров
down:
	docker compose down

# Остановка и удаление тестовых контейнеров
down-tests:
	docker compose -f docker-compose.test.yml down
