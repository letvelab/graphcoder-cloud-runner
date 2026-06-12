PYTHONPATH := apps/api/src:apps/worker/src:packages/common/src
REDIS_URL := redis://localhost:6379/0
JOBS_FILE := data/jobs.json

.PHONY: help init test lint format check run-api run-worker run-worker-once redis-up redis-down redis-logs docker-build docker-up docker-down docker-logs docker-ps clean-data

help:
	@echo "Available commands:"
	@echo "  make init             - Install dependencies"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run flake8"
	@echo "  make format           - Run black and isort"
	@echo "  make check            - Run format check, lint, and tests"
	@echo "  make run-api          - Run FastAPI locally with Redis queue"
	@echo "  make run-worker       - Run worker locally with Redis queue"
	@echo "  make run-worker-once  - Process one queued job and exit"
	@echo "  make redis-up         - Start Redis using Docker Compose"
	@echo "  make redis-down       - Stop Redis"
	@echo "  make redis-logs       - Show Redis logs"
	@echo "  make docker-build     - Build API and worker Docker images"
	@echo "  make docker-up        - Start full local stack"
	@echo "  make docker-down      - Stop full local stack"
	@echo "  make docker-logs      - Show all Docker logs"
	@echo "  make docker-ps        - Show Docker containers"
	@echo "  make clean-data       - Remove local job data"

init:
	uv sync

test:
	PYTHONPATH=$(PYTHONPATH) uv run pytest

lint:
	PYTHONPATH=$(PYTHONPATH) uv run flake8 apps packages tests

format:
	PYTHONPATH=$(PYTHONPATH) uv run black apps packages tests
	PYTHONPATH=$(PYTHONPATH) uv run isort apps packages tests

check:
	PYTHONPATH=$(PYTHONPATH) uv run black --check apps packages tests
	PYTHONPATH=$(PYTHONPATH) uv run isort --check-only apps packages tests
	PYTHONPATH=$(PYTHONPATH) uv run flake8 apps packages tests
	PYTHONPATH=$(PYTHONPATH) uv run pytest

run-api:
	PYTHONPATH=$(PYTHONPATH) REDIS_URL=$(REDIS_URL) JOBS_FILE=$(JOBS_FILE) uv run uvicorn graphcoder_api.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	PYTHONPATH=$(PYTHONPATH) REDIS_URL=$(REDIS_URL) JOBS_FILE=$(JOBS_FILE) uv run python -m graphcoder_worker.main

run-worker-once:
	PYTHONPATH=$(PYTHONPATH) REDIS_URL=$(REDIS_URL) JOBS_FILE=$(JOBS_FILE) uv run python -m graphcoder_worker.main --once

redis-up:
	docker compose up -d redis

redis-down:
	docker compose down

redis-logs:
	docker compose logs -f redis

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-ps:
	docker compose ps

clean-data:
	rm -rf data
