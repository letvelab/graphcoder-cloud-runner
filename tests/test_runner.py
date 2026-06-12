from graphcoder_common.jobs import JobCreateRequest, create_queued_job
from graphcoder_common.runner import MockGraphCoderRunner


def test_mock_runner_returns_successful_result() -> None:
    request = JobCreateRequest(
        task="Create a FastAPI app with a health endpoint",
    )
    job = create_queued_job(request)
    runner = MockGraphCoderRunner()

    result = runner.run(job)

    assert result.tests_passed is True
    assert "Mock GraphCoder completed dry-run" in result.summary
    assert result.generated_files == [
        "SPEC.md",
        "main.py",
        "tests/test_main.py",
    ]
