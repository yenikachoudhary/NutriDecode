
from fastapi.testclient import TestClient

from app.main import app
from app.api import analyze as analyze_api

client = TestClient(app)


def test_image_analysis_includes_name_resolution(monkeypatch):
    monkeypatch.setattr(
        analyze_api,
        "extract_text",
        lambda image_bytes: {
            "extracted_text": "Ingredients: haldi, uppu",
            "character_count": 24,
            "has_text": True,
        },
    )

    monkeypatch.setattr(
        analyze_api,
        "analyze_ingredients",
        lambda text: {
            "ingredients": [
                {
                    "raw_text": "haldi",
                    "normalized_name": "haldi",
                    "recognized": False,
                    "review_required": True,
                },
                {
                    "raw_text": "uppu",
                    "normalized_name": "uppu",
                    "recognized": False,
                    "review_required": True,
                },
            ],
            "additives": [],
            "additive_codes_found": [],
            "review_required": True,
            "disclaimer": "Identification only.",
        },
    )

    response = client.post(
        "/api/v1/analyze/image",
        files={"file": ("label.png", b"fake image", "image/png")},
    )

    assert response.status_code == 200

    ingredients = response.json()["ingredients"]

    assert ingredients[0]["name_resolution"]["canonical_name"] == "turmeric"
    assert ingredients[1]["name_resolution"]["canonical_name"] == "salt"
    assert ingredients[0]["name_resolution"]["matched"] is True
