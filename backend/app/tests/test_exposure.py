import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.exposure_service import calculate_exposure

client = TestClient(app)


def test_calculates_exposure_and_adi_percentage():
    result = calculate_exposure(
        concentration_mg_per_kg_food=100,
        serving_size_g=50,
        body_weight_kg=60,
        adi_mg_per_kg_body_weight_day=1,
        servings_per_day=2,
    )

    assert result["estimated_intake_mg_per_day"] == 10
    assert result["estimated_exposure_mg_per_kg_body_weight_day"] == pytest.approx(
        10 / 60, abs=0.000001
    )
    assert result["adi_percentage"] == pytest.approx(16.67)
    assert result["status"] == "estimated"


def test_reports_when_estimate_exceeds_adi():
    result = calculate_exposure(1000, 100, 50, 1)

    assert result["adi_percentage"] == 200
    assert "above" in result["interpretation"]


def test_rejects_zero_body_weight():
    with pytest.raises(ValueError):
        calculate_exposure(100, 50, 0, 1)


def test_rejects_negative_concentration():
    with pytest.raises(ValueError):
        calculate_exposure(-1, 50, 60, 1)


def test_exposure_api_endpoint():
    response = client.post(
        "/api/v1/exposure/calculate",
        json={
            "concentration_mg_per_kg_food": 500,
            "serving_size_g": 30,
            "body_weight_kg": 60,
            "adi_mg_per_kg_body_weight_day": 5.0,
            "servings_per_day": 1.0,
            "additive_code": "211",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "estimated"
    assert data["estimated_intake_mg_per_day"] == 15.0
    assert data["estimated_exposure_mg_per_kg_body_weight_day"] == 0.25
    assert data["adi_percentage"] == 5.0
    assert data["additive_code"] == "211"


def test_exposure_api_rejects_invalid_values():
    response = client.post(
        "/api/v1/exposure/calculate",
        json={
            "concentration_mg_per_kg_food": -10,
            "serving_size_g": 30,
            "body_weight_kg": 60,
            "adi_mg_per_kg_body_weight_day": 5.0,
        },
    )
    assert response.status_code == 422


def test_reference_adi_endpoint():
    response = client.get("/api/v1/exposure/reference-adi/334")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "334"
    assert data["adi_value_numeric"] == 30.0
    assert data["is_calculable"] is True


def test_reference_adi_gmp_endpoint():
    response = client.get("/api/v1/exposure/reference-adi/330")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "330"
    assert data["adi_value_numeric"] is None
    assert data["is_calculable"] is False
    assert "not specified" in data["adi_text"].lower()


def test_list_reference_adis_endpoint():
    response = client.get("/api/v1/exposure/reference-adis")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 5
    codes = {item["code"] for item in items}
    assert "330" in codes
    assert "334" in codes
