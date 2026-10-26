
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_evidence():
    response = client.get("/api/v1/evidence")

    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 5
    assert len(data["records"]) == 5


def test_single_additive_has_sources():
    response = client.get("/api/v1/evidence/330")

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Citric acid"
    assert data["safety_conclusion"] is None
    assert "fssai" in data["sources"]
    assert "jecfa" in data["sources"]


def test_unknown_additive_returns_404():
    response = client.get("/api/v1/evidence/9999")

    assert response.status_code == 404
