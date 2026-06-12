from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobMode(StrEnum):
    DRY_RUN = "dry_run"
    SANDBOXED = "sandboxed"


class JobRunResult(BaseModel):
    summary: str
    generated_files: list[str] = Field(default_factory=list)
    tests_passed: bool


class JobCreateRequest(BaseModel):
    task: str = Field(
        ...,
        min_length=3,
        max_length=4000,
        description="User request for GraphCoder.",
    )
    mode: JobMode = Field(
        default=JobMode.DRY_RUN,
        description="Execution mode. Dry-run does not execute generated code.",
    )


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    task: str
    mode: JobMode
    created_at: datetime
    updated_at: datetime
    result: JobRunResult | None = None
    error_message: str | None = None


def utc_now() -> datetime:
    return datetime.now(UTC)


def create_queued_job(request: JobCreateRequest) -> JobResponse:
    now = utc_now()

    return JobResponse(
        job_id=f"job_{uuid4().hex}",
        status=JobStatus.QUEUED,
        task=request.task,
        mode=request.mode,
        created_at=now,
        updated_at=now,
    )


def mark_job_running(job: JobResponse) -> JobResponse:
    return job.model_copy(
        update={
            "status": JobStatus.RUNNING,
            "updated_at": utc_now(),
        }
    )


def mark_job_succeeded(job: JobResponse, result: JobRunResult) -> JobResponse:
    return job.model_copy(
        update={
            "status": JobStatus.SUCCEEDED,
            "updated_at": utc_now(),
            "result": result,
            "error_message": None,
        }
    )


def mark_job_failed(job: JobResponse, error_message: str) -> JobResponse:
    return job.model_copy(
        update={
            "status": JobStatus.FAILED,
            "updated_at": utc_now(),
            "error_message": error_message,
        }
    )
