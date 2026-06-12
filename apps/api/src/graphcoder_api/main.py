from fastapi import FastAPI, HTTPException, status
from graphcoder_api.services import JobExecutionService
from graphcoder_api.storage import InMemoryJobRepository, JobNotFoundError
from graphcoder_common.jobs import JobCreateRequest, JobResponse, create_queued_job
from graphcoder_common.runner import MockGraphCoderRunner
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


job_repository = InMemoryJobRepository()
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
        return job_repository.save(job)

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
