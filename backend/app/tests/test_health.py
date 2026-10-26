
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Welcome to NutriDecode API"
    assert data["docs"] == "/docs"
    assert data["health"] == "/api/v1/health"


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["app"] == "NutriDecode API"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "development"


def test_api_documentation_is_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert "/api/v1/health" in schema["paths"]
