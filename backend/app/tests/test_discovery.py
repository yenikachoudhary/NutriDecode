import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.product_discovery_service import (
    calculate_data_completeness,
    detect_record_conflicts,
    get_additive_discovery_guidance,
    search_candidate_products,
)

client = TestClient(app)


def test_data_completeness_calculation():
    # Complete product
    full_product = {
        "name": "Organic Whole Wheat Crackers",
        "brands": "HealthyFarm",
        "front_image_url": "https://example.com/front.jpg",
        "ingredients_text": "Wheat flour, sunflower oil, sea salt.",
        "nutrition_per_100g": {
            "energy_kcal": 420,
            "sugars_g": 2.5,
            "salt_g": 1.1,
        },
    }
    score = calculate_data_completeness(full_product)
    assert score >= 80

    # Minimal product
    sparse_product = {
        "name": "Generic Biscuit",
    }
    score_sparse = calculate_data_completeness(sparse_product)
    assert score_sparse == 15


def test_record_conflicts_detection():
    # No conflicts
    assert detect_record_conflicts([]) == []
    assert detect_record_conflicts([{"brands": "BrandA"}]) == []

    # Divergent brands conflict
    candidates = [
        {"brands": "Brand Alpha", "ingredients_snippet": "Flour, salt"},
        {"brands": "Brand Beta", "ingredients_snippet": "Flour, salt"},
    ]
    conflicts = detect_record_conflicts(candidates)
    assert len(conflicts) >= 1
    assert "Multiple differing brands" in conflicts[0]

    # Differing ingredient formulations
    candidates_formulations = [
        {"brands": "Brand Alpha", "ingredients_snippet": "Flour, palm oil, salt"},
        {"brands": "Brand Alpha", "ingredients_snippet": "Flour, butter, salt"},
    ]
    conflicts_formulations = detect_record_conflicts(candidates_formulations)
    assert any("Differing ingredient formulations" in c for c in conflicts_formulations)


@pytest.mark.asyncio
async def test_search_candidate_products_mocked():
    mock_payload = {
        "products": [
            {
                "code": "8901234567890",
                "product_name": "Indian Spiced Masala Chips",
                "brands": "DesiSnacks",
                "quantity": "50g",
                "image_front_url": "https://example.com/desi.jpg",
                "ingredients_text": "Potatoes, edible vegetable oil, salt, spices, INS 330.",
                "nutriments": {"energy-kcal_100g": 520, "sugars_100g": 3.0, "salt_100g": 1.5},
                "nutrition_grades": "d",
            }
        ]
    }

    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.raise_for_status = lambda: None
    mock_response.json = lambda: mock_payload
    mock_client.get = AsyncMock(return_value=mock_response)

    result = await search_candidate_products("masala chips", client=mock_client)

    assert result["candidates_found"] == 1
    candidate = result["candidates"][0]
    assert candidate["barcode"] == "8901234567890"
    assert candidate["name"] == "Indian Spiced Masala Chips"
    assert candidate["is_verified_match"] is False
    assert candidate["data_completeness_percent"] > 60
    assert "Unverified candidate record" in candidate["action_prompt"] or "Candidate record found" in candidate["action_prompt"]


def test_products_search_endpoint(monkeypatch):
    async def mock_search(query, client=None, limit=5):
        return {
            "query": query,
            "candidates_found": 1,
            "candidates": [
                {
                    "barcode": "8901111111111",
                    "name": "Sample Tea Biscuits",
                    "brands": "Parle",
                    "data_completeness_percent": 85,
                    "is_verified_match": False,
                    "source": "Open Food Facts Registry Search",
                }
            ],
            "conflicts_detected": [],
            "retrieval_timestamp": "2026-10-27T00:00:00Z",
            "message": "Found 1 candidate product record(s).",
        }

    from app.api import products as products_api
    monkeypatch.setattr(products_api, "search_candidate_products", mock_search)

    response = client.get("/api/v1/products/search?query=parle&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["candidates_found"] == 1
    assert data["candidates"][0]["name"] == "Sample Tea Biscuits"


def test_additive_discovery_guidance():
    # Numeric ADI
    numeric_ev = {"adi": {"status": "numeric", "value": 30.0}}
    res_num = get_additive_discovery_guidance("334", numeric_ev)
    assert res_num["has_numeric_adi"] is True
    assert res_num["guidance_type"] == "verified_adi_available"

    # GMP / Not specified
    gmp_ev = {"adi": {"status": "not_specified", "value": None}}
    res_gmp = get_additive_discovery_guidance("330", gmp_ev)
    assert res_gmp["has_numeric_adi"] is False
    assert res_gmp["guidance_type"] == "gmp_additive"
    assert "Good Manufacturing Practice" in res_gmp["recommendation"]

    # Uncatalogued additive
    res_unknown = get_additive_discovery_guidance("999", None)
    assert res_unknown["has_numeric_adi"] is False
    assert res_unknown["guidance_type"] == "uncatalogued_additive"
    assert "jecfa-database" in res_unknown["source_search_url"]
