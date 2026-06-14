PYTHONPATH := apps/api/src:apps/worker/src:packages/common/src
REDIS_URL := redis://localhost:6379/0
JOBS_FILE := data/jobs.json
TF_DEV_DIR := infra/terraform/envs/dev
TF_DEV_DIR := infra/terraform/envs/dev
AWS_REGION := eu-central-1
PROJECT_NAME := gcr-runner
ENVIRONMENT := dev
AWS_PROFILE ?= ai-langgraph
AWS_REGION ?= eu-central-1
ECR_API_REPOSITORY := $(PROJECT_NAME)-$(ENVIRONMENT)-api
ECR_WORKER_REPOSITORY := $(PROJECT_NAME)-$(ENVIRONMENT)-worker
EKS_CLUSTER_NAME := $(PROJECT_NAME)-$(ENVIRONMENT)-eks

IMAGE_TAG ?= latest



.PHONY: help init test lint format check run-api run-worker run-worker-once redis-up redis-down redis-logs docker-build docker-up docker-down docker-logs docker-ps clean-data tf-init tf-fmt tf-validate tf-plan tf-apply tf-destroy aws-whoami ecr-login ecr-build-local ecr-tag ecr-push tf-init-upgrade eks-update-kubeconfig eks-nodes eks-pods eks-cluster-info

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
	@echo "  make tf-init          - Initialize Terraform dev environment"
	@echo "  make tf-fmt           - Format Terraform files"
	@echo "  make tf-validate      - Validate Terraform configuration"
	@echo "  make tf-plan          - Show Terraform execution plan"
	@echo "  make tf-apply         - Apply Terraform changes"
	@echo "  make tf-destroy       - Destroy Terraform-managed resources"
	@echo "  make aws-whoami       - Show current AWS identity"
	@echo "  make ecr-login        - Login Docker to AWS ECR"
	@echo "  make ecr-build-local  - Build local API and worker images"
	@echo "  make ecr-tag          - Tag local images for ECR"
	@echo "  make ecr-push         - Push images to ECR"
	@echo "  make tf-init-upgrade       - Reinitialize Terraform and upgrade providers/modules"
	@echo "  make eks-update-kubeconfig - Configure kubectl for EKS"
	@echo "  make eks-nodes             - Show EKS nodes"
	@echo "  make eks-pods              - Show all Kubernetes pods"
	@echo "  make eks-cluster-info      - Show Kubernetes cluster info"

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

tf-init:
	cd $(TF_DEV_DIR) && terraform init

tf-fmt:
	cd $(TF_DEV_DIR) && terraform fmt -recursive

tf-validate:
	cd $(TF_DEV_DIR) && terraform validate

tf-plan:
	cd $(TF_DEV_DIR) && terraform plan

tf-apply:
	cd $(TF_DEV_DIR) && terraform apply

tf-destroy:
	cd $(TF_DEV_DIR) && terraform destroy

aws-whoami:
	aws sts get-caller-identity

ecr-login:
	ACCOUNT_ID=$$(AWS_PROFILE=$(AWS_PROFILE) aws sts get-caller-identity --query Account --output text); \
	ECR_REGISTRY=$$ACCOUNT_ID.dkr.ecr.$(AWS_REGION).amazonaws.com; \
	AWS_PROFILE=$(AWS_PROFILE) aws ecr get-login-password --region $(AWS_REGION) | \
	docker login --username AWS --password-stdin $$ECR_REGISTRY

ecr-tag:
	ACCOUNT_ID=$$(AWS_PROFILE=$(AWS_PROFILE) aws sts get-caller-identity --query Account --output text); \
	ECR_REGISTRY=$$ACCOUNT_ID.dkr.ecr.$(AWS_REGION).amazonaws.com; \
	docker tag graphcoder-api:local $$ECR_REGISTRY/$(ECR_API_REPOSITORY):$(IMAGE_TAG); \
	docker tag graphcoder-worker:local $$ECR_REGISTRY/$(ECR_WORKER_REPOSITORY):$(IMAGE_TAG)

ecr-push: ecr-login ecr-tag
	ACCOUNT_ID=$$(AWS_PROFILE=$(AWS_PROFILE) aws sts get-caller-identity --query Account --output text); \
	ECR_REGISTRY=$$ACCOUNT_ID.dkr.ecr.$(AWS_REGION).amazonaws.com; \
	docker push $$ECR_REGISTRY/$(ECR_API_REPOSITORY):$(IMAGE_TAG); \
	docker push $$ECR_REGISTRY/$(ECR_WORKER_REPOSITORY):$(IMAGE_TAG)

tf-init-upgrade:
	cd $(TF_DEV_DIR) && terraform init -upgrade

eks-update-kubeconfig:
	aws eks update-kubeconfig --region $(AWS_REGION) --name $(EKS_CLUSTER_NAME)

eks-nodes:
	kubectl get nodes -o wide

eks-pods:
	kubectl get pods -A

eks-cluster-info:
	kubectl cluster-info
