
dev:
	fastapi dev src

run:
	fastapi run src

up:
	docker compose up -d

down:
	docker compose down

format:
	isort .
	black .
