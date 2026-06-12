import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from graphcoder_api.services import JobExecutionService
from graphcoder_common.jobs import JobCreateRequest, JobResponse, create_queued_job
from graphcoder_common.queue import InMemoryJobQueue, JobQueue, RedisJobQueue
from graphcoder_common.runner import MockGraphCoderRunner
from graphcoder_common.storage import FileJobRepository, JobNotFoundError
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


def build_job_repository() -> FileJobRepository:
    jobs_file = Path(os.getenv("JOBS_FILE", "data/jobs.json"))
    return FileJobRepository(path=jobs_file)


def build_job_queue() -> JobQueue:
    redis_url = os.getenv("REDIS_URL")

    if redis_url:
        return RedisJobQueue(redis_url=redis_url)

    return InMemoryJobQueue()


job_repository = build_job_repository()
job_queue = build_job_queue()
graphcoder_runner = MockGraphCoderRunner()
job_execution_service = JobExecutionService(
    repository=job_repository,
    runner=graphcoder_runner,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="GraphCoder Cloud Runner API",
        version="0.1.0",
        description="API service for submitting and tracking GraphCoder jobs.",
    )

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="graphcoder-api",
            version="0.1.0",
        )

    @app.post(
        "/jobs",
        response_model=JobResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["jobs"],
    )
    async def create_job(request: JobCreateRequest) -> JobResponse:
        job = create_queued_job(request)
        saved_job = job_repository.save(job)

        await job_queue.enqueue(saved_job.job_id)

        return saved_job

    @app.get("/jobs/{job_id}", response_model=JobResponse, tags=["jobs"])
    async def get_job(job_id: str) -> JobResponse:
        try:
            return job_repository.get(job_id)
        except JobNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            ) from exc

    @app.post("/jobs/{job_id}/run", response_model=JobResponse, tags=["jobs"])
    async def run_job(job_id: str) -> JobResponse:
        try:
            return job_execution_service.run_job(job_id)
        except JobNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            ) from exc

    return app


app = create_app()
