from fastapi.testclient import TestClient
from graphcoder_api.main import app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "graphcoder-api",
        "version": "0.1.0",
    }
