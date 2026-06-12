import argparse
import asyncio
import json
import os
from pathlib import Path

from graphcoder_api.services import JobExecutionService
from graphcoder_common.jobs import JobResponse
from graphcoder_common.queue import InMemoryJobQueue, JobQueue, RedisJobQueue
from graphcoder_common.runner import MockGraphCoderRunner
from graphcoder_common.storage import FileJobRepository, JobNotFoundError, JobRepository


def log_event(event: str, **fields: object) -> None:
    payload = {
        "event": event,
        **fields,
    }
    print(json.dumps(payload), flush=True)


def process_job_by_id(
    job_id: str,
    execution_service: JobExecutionService,
) -> JobResponse | None:
    try:
        log_event("job_started", job_id=job_id)
        completed_job = execution_service.run_job(job_id)
    except JobNotFoundError:
        log_event("job_not_found", job_id=job_id)
        return None

    log_event(
        "job_finished",
        job_id=completed_job.job_id,
        status=completed_job.status,
    )

    return completed_job


async def run_worker(
    queue: JobQueue,
    execution_service: JobExecutionService,
    dequeue_timeout_seconds: int,
    once: bool,
) -> None:
    log_event("worker_started", once=once)

    while True:
        job_id = await queue.dequeue(timeout_seconds=dequeue_timeout_seconds)

        if job_id is None:
            log_event("no_jobs_available")

            if once:
                return

            continue

        process_job_by_id(
            job_id=job_id,
            execution_service=execution_service,
        )

        if once:
            return


def build_repository() -> FileJobRepository:
    jobs_file = Path(os.getenv("JOBS_FILE", "data/jobs.json"))
    return FileJobRepository(path=jobs_file)


def build_queue() -> JobQueue:
    redis_url = os.getenv("REDIS_URL")

    if redis_url:
        return RedisJobQueue(redis_url=redis_url)

    return InMemoryJobQueue()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GraphCoder worker process")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process one queued job and exit",
    )
    parser.add_argument(
        "--dequeue-timeout",
        type=int,
        default=5,
        help="Redis BLPOP timeout in seconds",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    repository: JobRepository = build_repository()
    queue = build_queue()
    runner = MockGraphCoderRunner()

    execution_service = JobExecutionService(
        repository=repository,
        runner=runner,
    )

    asyncio.run(
        run_worker(
            queue=queue,
            execution_service=execution_service,
            dequeue_timeout_seconds=args.dequeue_timeout,
            once=args.once,
        )
    )


if __name__ == "__main__":
    main()
