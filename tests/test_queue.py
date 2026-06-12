from graphcoder_common.queue import InMemoryJobQueue


async def test_in_memory_queue_enqueues_and_dequeues_job_id() -> None:
    queue = InMemoryJobQueue()

    await queue.enqueue("job_123")

    job_id = await queue.dequeue(timeout_seconds=0)

    assert job_id == "job_123"


async def test_in_memory_queue_returns_none_when_empty() -> None:
    queue = InMemoryJobQueue()

    job_id = await queue.dequeue(timeout_seconds=0)

    assert job_id is None
