from fastapi.testclient import TestClient
from graphcoder_api.main import app, job_repository


def setup_function() -> None:
    job_repository.clear()


def test_create_job_returns_queued_job() -> None:
    client = TestClient(app)

    response = client.post(
        "/jobs",
        json={
            "task": "Create a FastAPI app with a health endpoint",
            "mode": "dry_run",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["job_id"].startswith("job_")
    assert body["status"] == "queued"
    assert body["task"] == "Create a FastAPI app with a health endpoint"
    assert body["mode"] == "dry_run"
    assert body["result"] is None
    assert body["error_message"] is None
    assert "created_at" in body
    assert "updated_at" in body


def test_get_existing_job_returns_job() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/jobs",
        json={
            "task": "Generate pytest tests for existing code",
        },
    )

    created_job = create_response.json()
    job_id = created_job["job_id"]

    get_response = client.get(f"/jobs/{job_id}")

    assert get_response.status_code == 200
    assert get_response.json() == created_job


def test_get_missing_job_returns_404() -> None:
    client = TestClient(app)

    response = client.get("/jobs/job_missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}


def test_create_job_rejects_empty_task() -> None:
    client = TestClient(app)

    response = client.post(
        "/jobs",
        json={
            "task": "",
            "mode": "dry_run",
        },
    )

    assert response.status_code == 422


def test_create_job_rejects_unknown_mode() -> None:
    client = TestClient(app)

    response = client.post(
        "/jobs",
        json={
            "task": "Create a small Python project",
            "mode": "dangerous_mode",
        },
    )

    assert response.status_code == 422


def test_run_job_endpoint_marks_job_as_succeeded() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/jobs",
        json={
            "task": "Create a FastAPI app with /health endpoint",
            "mode": "dry_run",
        },
    )

    created_job = create_response.json()
    job_id = created_job["job_id"]

    run_response = client.post(f"/jobs/{job_id}/run")

    assert run_response.status_code == 200

    body = run_response.json()

    assert body["job_id"] == job_id
    assert body["status"] == "succeeded"
    assert body["result"] is not None
    assert body["result"]["tests_passed"] is True
    assert body["error_message"] is None
