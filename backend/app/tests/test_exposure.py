
import pytest

from app.services.exposure_service import calculate_exposure


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
