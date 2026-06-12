# GraphCoder Cloud Runner

A cloud-native platform for running GraphCoder jobs using FastAPI, async workers, Kubernetes, AWS EKS, and Terraform.

## Goal

The goal of this project is to demonstrate practical DevOps and platform engineering skills:

- FastAPI service design
- Async job processing
- Docker-based local development
- Kubernetes deployment
- AWS EKS infrastructure with Terraform
- CI/CD with GitHub Actions
- Observability, security, and cost-aware cloud usage

## Architecture

```text
User
  |
  v
FastAPI API
  |
  v
Queue
  |
  v
GraphCoder Worker
  |
  v
Artifacts / Logs / Job Status
Planned AWS Components
EKS
ECR
S3
IAM
CloudWatch
Application Load Balancer
Cost Control

This project is designed to avoid unnecessary AWS costs.

Rules:

Develop locally first.
Use EKS only when needed.
Destroy cloud infrastructure after testing.
Avoid expensive always-on resources where possible.
Keep CloudWatch log retention short.


---

## `docs/adr/0001-architecture.md`

ADR — це хороший сигнал на співбесіді. Показує, що ти мислиш як інженер, а не просто “пишеш yaml”.

```md
# ADR 0001: Use API + Worker Architecture

## Status

Accepted

## Context

GraphCoder jobs may be long-running and potentially resource-intensive.
Running them synchronously inside the API process would make the API slow,
harder to scale, and less reliable.

## Decision

We will split the system into two main services:

1. FastAPI API service
2. GraphCoder worker service

The API will accept job requests and return a job ID.
The worker will process jobs asynchronously.

## Consequences

Positive:

- API remains fast and responsive.
- Workers can be scaled independently.
- Long-running jobs do not block HTTP requests.
- The architecture maps well to Kubernetes and cloud deployments.

Negative:

- More moving parts.
- Need queue/storage for job state.
- More operational complexity.
