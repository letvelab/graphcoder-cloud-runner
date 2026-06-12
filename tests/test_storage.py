from graphcoder_common.jobs import JobCreateRequest, JobStatus, create_queued_job
from graphcoder_common.storage import FileJobRepository


def test_file_repository_saves_and_loads_job(tmp_path) -> None:
    repository = FileJobRepository(path=tmp_path / "jobs.json")

    job = create_queued_job(JobCreateRequest(task="Create a FastAPI health endpoint"))

    repository.save(job)

    loaded_job = repository.get(job.job_id)

    assert loaded_job == job


def test_file_repository_lists_jobs_by_status(tmp_path) -> None:
    repository = FileJobRepository(path=tmp_path / "jobs.json")

    job = create_queued_job(JobCreateRequest(task="Create a FastAPI health endpoint"))

    repository.save(job)

    queued_jobs = repository.list_by_status(JobStatus.QUEUED)

    assert queued_jobs == [job]
