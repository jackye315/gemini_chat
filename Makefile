ENV = --env-file .env
APP = -f ./docker/docker-compose.yaml

up:
	docker compose $(APP) $(ENV) up -d

down:
	docker compose $(APP) $(ENV) down

rebuild:
	docker compose $(APP) $(ENV) build --no-cache