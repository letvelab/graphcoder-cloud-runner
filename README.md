# GraphCoder Cloud Runner

A small cloud-native job runner for GraphCoder-style coding tasks.

The project is intentionally built as a platform engineering / DevOps practice project. It starts locally with Docker Compose, then runs on Kubernetes, and finally can be deployed to AWS EKS using Terraform-managed infrastructure.

## What it does

The system exposes a FastAPI service where a user can submit a coding task. The task is stored as a job, pushed into a Redis queue, and processed asynchronously by a separate worker.

Current runner implementation is a mock GraphCoder runner. The goal of this repository is not to build the final AI coding agent yet, but to build the infrastructure and runtime model around it.

## Architecture

```text
Client
  |
  v
FastAPI API
  |
  | create job
  | save job state
  | enqueue job_id
  v
Redis
  ^
  | dequeue job_id
  | update job state
  |
Worker
  |
  v
GraphCoder Runner
```

Services:

- `api` — FastAPI application
- `worker` — background worker process
- `redis` — queue and job state storage

The API and worker are deployed as separate services. They are not placed into the same Kubernetes Pod because they have different lifecycle, scaling, and resource requirements.

## Tech stack

- Python 3.11
- FastAPI
- Pydantic v2
- Redis
- Docker
- Docker Compose
- Kubernetes
- Kustomize
- Terraform
- AWS ECR
- AWS EKS

Development tooling:

- uv
- pytest
- black
- isort
- flake8

## Repository structure

```text
.
├── apps/
│   ├── api/
│   │   └── src/graphcoder_api/
│   └── worker/
│       └── src/graphcoder_worker/
├── packages/
│   └── common/
│       └── src/graphcoder_common/
├── k8s/
│   ├── base/
│   └── overlays/
│       ├── local/
│       └── aws/
├── infra/
│   └── terraform/
│       ├── envs/dev/
│       └── modules/
├── Dockerfile.api
├── Dockerfile.worker
├── docker-compose.yml
├── Makefile
└── README.md
```

## Local development

Install dependencies:

```bash
make init
```

Run checks:

```bash
make format
make lint
make test
```

Run Redis locally:

```bash
make redis-up
```

Run API:

```bash
make run-api
```

Run worker:

```bash
make run-worker
```

Create a job:

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a FastAPI app with health endpoint and tests",
    "mode": "dry_run"
  }'
```

Check job status:

```bash
curl http://localhost:8000/jobs/<job_id>
```

## Run with Docker Compose

Build and start the full local stack:

```bash
make docker-up
```

This starts:

- Redis
- API
- worker

Health check:

```bash
curl http://localhost:8000/health
```

Create a job:

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a FastAPI app with health endpoint and tests",
    "mode": "dry_run"
  }'
```

Worker logs:

```bash
docker compose logs -f worker
```

Stop the stack:

```bash
make docker-down
```

## Kubernetes local run

The project can be deployed to a local Kubernetes cluster using `kind`.

Create cluster:

```bash
kind create cluster --name graphcoder
```

Build images:

```bash
docker compose build api worker
```

Load images into kind:

```bash
kind load docker-image graphcoder-api:local --name graphcoder
kind load docker-image graphcoder-worker:local --name graphcoder
```

Apply Kubernetes manifests:

```bash
kubectl apply -k k8s/base
```

Check resources:

```bash
kubectl get all -n graphcoder
```

Forward API locally:

```bash
kubectl port-forward -n graphcoder service/graphcoder-api 8000:80
```

Test:

```bash
curl http://localhost:8000/health
```

Clean up:

```bash
kubectl delete -k k8s/base
kind delete cluster --name graphcoder
```

## AWS infrastructure

AWS infrastructure is managed with Terraform.

Current AWS resources:

- VPC
- public subnets
- ECR repositories
- EKS cluster
- EKS managed node group

The dev EKS environment is intentionally minimal. It uses one small worker node and avoids NAT Gateway to keep costs lower.

This is a dev setup, not a production-grade network design.

Production would usually use:

- private subnets for worker nodes
- NAT Gateway or VPC endpoints
- external managed Redis
- stronger IAM boundaries
- proper ingress setup
- monitoring and alerting

## Terraform workflow

Initialize Terraform:

```bash
make tf-init-upgrade
```

Format and validate:

```bash
make tf-fmt
make tf-validate
```

Preview changes:

```bash
make tf-plan
```

Apply infrastructure:

```bash
make tf-apply
```

Configure kubectl for EKS:

```bash
make eks-update-kubeconfig
```

Check cluster:

```bash
make eks-nodes
make eks-pods
```

Destroy infrastructure:

```bash
make tf-destroy
```

## ECR workflow

Login to ECR:

```bash
make ecr-login
```

Build local images:

```bash
make ecr-build-local
```

Tag images for ECR:

```bash
make ecr-tag
```

Push images:

```bash
make ecr-push
```

The current ECR repositories are expected to follow this naming pattern:

```text
gcr-runner-dev-api
gcr-runner-dev-worker
```

## Deploy to EKS

The base Kubernetes manifests use local image names:

```text
graphcoder-api:local
graphcoder-worker:local
```

For AWS, `k8s/overlays/aws` replaces those local image names with ECR image URLs.

Preview the final Kubernetes manifests:

```bash
kubectl kustomize k8s/overlays/aws
```

Deploy to EKS:

```bash
kubectl apply -k k8s/overlays/aws
```

Check resources:

```bash
kubectl get all -n graphcoder
```

Watch Pods:

```bash
kubectl get pods -n graphcoder -w
```

Forward API:

```bash
kubectl port-forward -n graphcoder service/graphcoder-api 8000:80
```

Test API:

```bash
curl http://localhost:8000/health
```

Create a job:

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a FastAPI app with health endpoint and tests",
    "mode": "dry_run"
  }'
```

Check worker logs:

```bash
kubectl logs -n graphcoder deployment/graphcoder-worker -f
```

Delete application resources:

```bash
kubectl delete -k k8s/overlays/aws
```

## Cost notes

EKS is not free. The cluster control plane has an hourly cost, and worker nodes are regular EC2 instances.

For this reason, the dev workflow is:

```text
create infrastructure
deploy application
test
destroy infrastructure
```

Do not leave the EKS cluster running if it is not being used.

Useful cleanup commands:

```bash
kubectl delete -k k8s/overlays/aws
make tf-destroy
```

`kubectl delete` removes the application from Kubernetes.  
`make tf-destroy` removes AWS infrastructure managed by Terraform.

Both are important.

## Kubernetes design notes

The application uses separate Deployments:

- `graphcoder-api`
- `graphcoder-worker`
- `redis`

Each Pod runs a single main container.

This is deliberate. The API and worker are separate workloads. They can be restarted, scaled, and monitored independently.

Redis is exposed only inside the cluster through a `ClusterIP` Service. The API is also internal by default. For testing, access is done through `kubectl port-forward`.

## Useful Kubernetes commands

```bash
kubectl get all -n graphcoder
kubectl get pods -n graphcoder
kubectl describe pod -n graphcoder <pod-name>
kubectl logs -n graphcoder deployment/graphcoder-api
kubectl logs -n graphcoder deployment/graphcoder-worker
kubectl logs -n graphcoder deployment/redis
kubectl get events -n graphcoder --sort-by=.lastTimestamp
```

## Current limitations

This is still a learning/dev project.

Known limitations:

- Redis is used both as queue and job state storage.
- Redis runs inside the cluster.
- The GraphCoder runner is mocked.
- There is no public ingress yet.
- There is no authentication on the API.
- There is no persistent production database.
- There is no CI/CD deployment pipeline yet.

These are intentional for the current stage. The goal was to build a small but realistic deployment path before adding more production features.

## Next improvements

Possible next steps:

- Replace mock runner with real GraphCoder execution
- Add GitHub Actions for build/test/push/deploy
- Add Kubernetes Ingress or AWS Load Balancer Controller
- Add API authentication
- Move job state to PostgreSQL or DynamoDB
- Add Prometheus-style metrics
- Add structured request IDs
- Add HPA for API and worker
- Add separate staging/prod overlays

## Project status

Working end-to-end:

```text
FastAPI API -> Redis -> Worker -> Job result
```

Verified locally with Docker Compose and on AWS EKS.
