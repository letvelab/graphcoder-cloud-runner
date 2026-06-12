PYTHONPATH := apps/api/src:apps/worker/src:packages/common/src

.PHONY: help init test lint format check run-api run-worker

help:
	@echo "Available commands:"
	@echo "  make init        - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run flake8"
	@echo "  make format      - Run black and isort"
	@echo "  make check       - Run format check, lint, and tests"
	@echo "  make run-api     - Run FastAPI locally"
	@echo "  make run-worker  - Run worker locally"

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
	PYTHONPATH=$(PYTHONPATH) uv run uvicorn graphcoder_api.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	@echo "Worker is not implemented yet"
