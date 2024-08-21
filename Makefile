SERVER_PATH = $(shell pwd)

export SERVER_PATH


run_all:
	docker compose -f docker/docker-compose.yml up -d


run_server:
	docker compose -f docker/docker-compose.yml up -d --build server

run_db:
	docker compose -f docker/docker-compose.yml up -d --build db redis


kill_them:
	docker compose -f docker/docker-compose.yml down

dev_run:
	python3 run_echo.py
