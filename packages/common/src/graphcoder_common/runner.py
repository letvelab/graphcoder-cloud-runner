from typing import Protocol

from graphcoder_common.jobs import JobResponse, JobRunResult


class GraphCoderRunner(Protocol):
    def run(self, job: JobResponse) -> JobRunResult:
        pass


class MockGraphCoderRunner:
    def run(self, job: JobResponse) -> JobRunResult:
        task_preview = job.task.strip().replace("\n", " ")[:120]

        return JobRunResult(
            summary=f"Mock GraphCoder completed dry-run for task: {task_preview}",
            generated_files=[
                "SPEC.md",
                "main.py",
                "tests/test_main.py",
            ],
            tests_passed=True,
        )
