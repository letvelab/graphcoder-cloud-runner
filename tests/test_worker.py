from graphcoder_api.services import JobExecutionService
from graphcoder_common.jobs import JobCreateRequest, JobStatus, create_queued_job
from graphcoder_common.runner import MockGraphCoderRunner
from graphcoder_common.storage import FileJobRepository
from graphcoder_worker.main import process_next_queued_job


def test_worker_processes_next_queued_job(tmp_path) -> None:
    repository = FileJobRepository(path=tmp_path / "jobs.json")
    runner = MockGraphCoderRunner()
    execution_service = JobExecutionService(
        repository=repository,
        runner=runner,
    )

    job = repository.save(
        create_queued_job(JobCreateRequest(task="Create a FastAPI health endpoint"))
    )

    completed_job = process_next_queued_job(
        repository=repository,
        execution_service=execution_service,
    )

    assert completed_job is not None
    assert completed_job.job_id == job.job_id
    assert completed_job.status == JobStatus.SUCCEEDED
    assert completed_job.result is not None

    stored_job = repository.get(job.job_id)

    assert stored_job.status == JobStatus.SUCCEEDED


def test_worker_returns_none_when_no_queued_jobs(tmp_path) -> None:
    repository = FileJobRepository(path=tmp_path / "jobs.json")
    runner = MockGraphCoderRunner()
    execution_service = JobExecutionService(
        repository=repository,
        runner=runner,
    )

    completed_job = process_next_queued_job(
        repository=repository,
        execution_service=execution_service,
    )

    assert completed_job is None
