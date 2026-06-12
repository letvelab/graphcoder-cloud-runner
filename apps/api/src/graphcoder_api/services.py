from graphcoder_common.jobs import (
    JobResponse,
    mark_job_failed,
    mark_job_running,
    mark_job_succeeded,
)
from graphcoder_common.runner import GraphCoderRunner
from graphcoder_common.storage import JobRepository


class JobExecutionService:
    def __init__(
        self,
        repository: JobRepository,
        runner: GraphCoderRunner,
    ) -> None:
        self._repository = repository
        self._runner = runner

    def run_job(self, job_id: str) -> JobResponse:
        job = self._repository.get(job_id)

        running_job = mark_job_running(job)
        self._repository.update(running_job)

        try:
            result = self._runner.run(running_job)
        except Exception as exc:
            failed_job = mark_job_failed(running_job, str(exc))
            return self._repository.update(failed_job)

        succeeded_job = mark_job_succeeded(running_job, result)
        return self._repository.update(succeeded_job)
