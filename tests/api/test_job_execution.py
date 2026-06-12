from graphcoder_api.services import JobExecutionService
from graphcoder_api.storage import InMemoryJobRepository
from graphcoder_common.jobs import (
    JobCreateRequest,
    JobResponse,
    JobStatus,
    create_queued_job,
)
from graphcoder_common.runner import MockGraphCoderRunner


def test_job_execution_service_marks_job_as_succeeded() -> None:
    repository = InMemoryJobRepository()
    runner = MockGraphCoderRunner()
    service = JobExecutionService(repository=repository, runner=runner)

    request = JobCreateRequest(
        task="Create a FastAPI app with /health endpoint",
    )
    job = repository.save(create_queued_job(request))

    completed_job = service.run_job(job.job_id)

    assert completed_job.status == JobStatus.SUCCEEDED
    assert completed_job.result is not None
    assert completed_job.result.tests_passed is True
    assert completed_job.error_message is None

    stored_job = repository.get(job.job_id)

    assert stored_job.status == JobStatus.SUCCEEDED
    assert stored_job.result is not None


def test_job_execution_service_marks_job_as_failed_when_runner_fails() -> None:
    class FailingRunner:
        def run(self, job: JobResponse):
            raise RuntimeError("GraphCoder failed")

    repository = InMemoryJobRepository()
    service = JobExecutionService(
        repository=repository,
        runner=FailingRunner(),
    )

    request = JobCreateRequest(
        task="Create a FastAPI app with /health endpoint",
    )
    job = repository.save(create_queued_job(request))

    failed_job = service.run_job(job.job_id)

    assert failed_job.status == JobStatus.FAILED
    assert failed_job.result is None
    assert failed_job.error_message == "GraphCoder failed"
