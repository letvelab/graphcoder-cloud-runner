import json
from pathlib import Path
from typing import Protocol

import redis

from graphcoder_common.jobs import JobResponse, JobStatus


class JobNotFoundError(Exception):
    pass


class JobRepository(Protocol):
    def save(self, job: JobResponse) -> JobResponse:
        pass

    def get(self, job_id: str) -> JobResponse:
        pass

    def update(self, job: JobResponse) -> JobResponse:
        pass

    def list_by_status(self, status: JobStatus) -> list[JobResponse]:
        pass

    def clear(self) -> None:
        pass


class InMemoryJobRepository:
    def __init__(self) -> None:
        self._jobs: dict[str, JobResponse] = {}

    def save(self, job: JobResponse) -> JobResponse:
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> JobResponse:
        job = self._jobs.get(job_id)

        if job is None:
            raise JobNotFoundError(f"Job not found: {job_id}")

        return job

    def update(self, job: JobResponse) -> JobResponse:
        if job.job_id not in self._jobs:
            raise JobNotFoundError(f"Job not found: {job.job_id}")

        self._jobs[job.job_id] = job
        return job

    def list_by_status(self, status: JobStatus) -> list[JobResponse]:
        return [job for job in self._jobs.values() if job.status == status]

    def clear(self) -> None:
        self._jobs.clear()


class FileJobRepository:
    """
    Local development repository.

    This is useful for simple local experiments, but it is NOT a good
    Kubernetes storage model because API and worker run in different Pods.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, job: JobResponse) -> JobResponse:
        jobs = self._load_all()
        jobs[job.job_id] = job
        self._write_all(jobs)
        return job

    def get(self, job_id: str) -> JobResponse:
        jobs = self._load_all()
        job = jobs.get(job_id)

        if job is None:
            raise JobNotFoundError(f"Job not found: {job_id}")

        return job

    def update(self, job: JobResponse) -> JobResponse:
        jobs = self._load_all()

        if job.job_id not in jobs:
            raise JobNotFoundError(f"Job not found: {job.job_id}")

        jobs[job.job_id] = job
        self._write_all(jobs)
        return job

    def list_by_status(self, status: JobStatus) -> list[JobResponse]:
        jobs = self._load_all()
        return [job for job in jobs.values() if job.status == status]

    def clear(self) -> None:
        self._write_all({})

    def _load_all(self) -> dict[str, JobResponse]:
        if not self._path.exists():
            return {}

        content = self._path.read_text(encoding="utf-8").strip()

        if not content:
            return {}

        raw_jobs = json.loads(content)

        return {
            raw_job["job_id"]: JobResponse.model_validate(raw_job)
            for raw_job in raw_jobs
        }

    def _write_all(self, jobs: dict[str, JobResponse]) -> None:
        tmp_path = self._path.with_name(f"{self._path.name}.tmp")

        raw_jobs = [
            job.model_dump(mode="json")
            for job in sorted(jobs.values(), key=lambda item: item.created_at)
        ]

        tmp_path.write_text(
            json.dumps(raw_jobs, indent=2),
            encoding="utf-8",
        )
        tmp_path.replace(self._path)


class RedisJobRepository:
    """
    Redis-backed job state repository.

    We use this for Docker Compose and Kubernetes because API and worker
    can both access Redis through the network.

    Data model:
      Redis hash:
        key: graphcoder:job-state
        field: job_id
        value: serialized JobResponse JSON
    """

    def __init__(
        self,
        redis_url: str,
        key: str = "graphcoder:job-state",
    ) -> None:
        self._redis = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
        )
        self._key = key

    def save(self, job: JobResponse) -> JobResponse:
        self._redis.hset(
            self._key,
            job.job_id,
            self._serialize(job),
        )
        return job

    def get(self, job_id: str) -> JobResponse:
        raw_job = self._redis.hget(self._key, job_id)

        if raw_job is None:
            raise JobNotFoundError(f"Job not found: {job_id}")

        return self._deserialize(raw_job)

    def update(self, job: JobResponse) -> JobResponse:
        if not self._redis.hexists(self._key, job.job_id):
            raise JobNotFoundError(f"Job not found: {job.job_id}")

        self._redis.hset(
            self._key,
            job.job_id,
            self._serialize(job),
        )
        return job

    def list_by_status(self, status: JobStatus) -> list[JobResponse]:
        raw_jobs = self._redis.hvals(self._key)

        jobs = [self._deserialize(raw_job) for raw_job in raw_jobs]

        return [job for job in jobs if job.status == status]

    def clear(self) -> None:
        self._redis.delete(self._key)

    def _serialize(self, job: JobResponse) -> str:
        return job.model_dump_json()

    def _deserialize(self, raw_job: str) -> JobResponse:
        return JobResponse.model_validate_json(raw_job)
