from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_liveness_returns_ok() -> None:
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Weekly Report API",
        "environment": "local",
    }