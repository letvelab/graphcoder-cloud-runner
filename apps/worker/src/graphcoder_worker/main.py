import argparse
import asyncio
import json
import os
from pathlib import Path

from graphcoder_api.services import JobExecutionService
from graphcoder_common.jobs import JobResponse, JobStatus
from graphcoder_common.runner import MockGraphCoderRunner
from graphcoder_common.storage import FileJobRepository, JobRepository


def log_event(event: str, **fields: object) -> None:
    payload = {
        "event": event,
        **fields,
    }
    print(json.dumps(payload), flush=True)


def process_next_queued_job(
    repository: JobRepository,
    execution_service: JobExecutionService,
) -> JobResponse | None:
    queued_jobs = repository.list_by_status(JobStatus.QUEUED)

    if not queued_jobs:
        return None

    job = queued_jobs[0]

    log_event(
        "job_started",
        job_id=job.job_id,
        mode=job.mode,
    )

    completed_job = execution_service.run_job(job.job_id)

    log_event(
        "job_finished",
        job_id=completed_job.job_id,
        status=completed_job.status,
    )

    return completed_job


async def run_worker(
    repository: JobRepository,
    execution_service: JobExecutionService,
    poll_interval_seconds: float,
    once: bool,
) -> None:
    log_event("worker_started", once=once)

    while True:
        completed_job = process_next_queued_job(
            repository=repository,
            execution_service=execution_service,
        )

        if once:
            if completed_job is None:
                log_event("no_queued_jobs")
            return

        await asyncio.sleep(poll_interval_seconds)


def build_repository() -> FileJobRepository:
    jobs_file = Path(os.getenv("JOBS_FILE", "data/jobs.json"))
    return FileJobRepository(path=jobs_file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GraphCoder worker process")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process one queued job and exit",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Polling interval in seconds",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    repository = build_repository()
    runner = MockGraphCoderRunner()
    execution_service = JobExecutionService(
        repository=repository,
        runner=runner,
    )

    asyncio.run(
        run_worker(
            repository=repository,
            execution_service=execution_service,
            poll_interval_seconds=args.poll_interval,
            once=args.once,
        )
    )


if __name__ == "__main__":
    main()
