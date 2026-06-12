from graphcoder_api.services import JobExecutionService
from graphcoder_common.jobs import JobCreateRequest, JobStatus, create_queued_job
from graphcoder_common.queue import InMemoryJobQueue
from graphcoder_common.runner import MockGraphCoderRunner
from graphcoder_common.storage import FileJobRepository
from graphcoder_worker.main import process_job_by_id, run_worker


def test_worker_processes_job_by_id(tmp_path) -> None:
    repository = FileJobRepository(path=tmp_path / "jobs.json")
    runner = MockGraphCoderRunner()
    execution_service = JobExecutionService(
        repository=repository,
        runner=runner,
    )

    job = repository.save(
        create_queued_job(JobCreateRequest(task="Create a FastAPI health endpoint"))
    )

    completed_job = process_job_by_id(
        job_id=job.job_id,
        execution_service=execution_service,
    )

    assert completed_job is not None
    assert completed_job.job_id == job.job_id
    assert completed_job.status == JobStatus.SUCCEEDED
    assert completed_job.result is not None

    stored_job = repository.get(job.job_id)

    assert stored_job.status == JobStatus.SUCCEEDED


async def test_worker_consumes_job_from_queue(tmp_path) -> None:
    repository = FileJobRepository(path=tmp_path / "jobs.json")
    queue = InMemoryJobQueue()
    runner = MockGraphCoderRunner()

    execution_service = JobExecutionService(
        repository=repository,
        runner=runner,
    )

    job = repository.save(
        create_queued_job(JobCreateRequest(task="Create a FastAPI health endpoint"))
    )

    await queue.enqueue(job.job_id)

    await run_worker(
        queue=queue,
        execution_service=execution_service,
        dequeue_timeout_seconds=0,
        once=True,
    )

    stored_job = repository.get(job.job_id)

    assert stored_job.status == JobStatus.SUCCEEDED
    assert stored_job.result is not None


async def test_worker_exits_when_queue_is_empty(tmp_path) -> None:
    repository = FileJobRepository(path=tmp_path / "jobs.json")
    queue = InMemoryJobQueue()
    runner = MockGraphCoderRunner()

    execution_service = JobExecutionService(
        repository=repository,
        runner=runner,
    )

    await run_worker(
        queue=queue,
        execution_service=execution_service,
        dequeue_timeout_seconds=0,
        once=True,
    )
