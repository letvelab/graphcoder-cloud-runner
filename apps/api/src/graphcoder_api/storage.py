from graphcoder_common.jobs import JobResponse


class JobNotFoundError(Exception):
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

    def clear(self) -> None:
        self._jobs.clear()
