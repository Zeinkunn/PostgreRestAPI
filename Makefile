.PHONY: build up down logs migrate test

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f api

migrate:
	docker-compose exec api alembic upgrade head

test:
	docker-compose exec api pytest tests/ -v
