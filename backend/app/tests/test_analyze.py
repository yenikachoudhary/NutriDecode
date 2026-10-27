from fastapi.testclient import TestClient

from app.main import app
from app.api import analyze as analyze_api

client = TestClient(app)


def test_image_analysis_includes_additive_evidence(monkeypatch):
    monkeypatch.setattr(
        analyze_api,
        "extract_text",
        lambda image_bytes: {
            "extracted_text": "Ingredients: Potato, Acidity Regulator (330)",
            "character_count": 42,
            "has_text": True,
        },
    )

    monkeypatch.setattr(
        analyze_api,
        "analyze_ingredients",
        lambda text: {
            "ingredients": [],
            "additives": [
                {
                    "code": "330",
                    "name": "Citric acid",
                    "purpose": "Acidity regulator",
                    "evidence_status": "identity_reference",
                    "safety_conclusion": None,
                }
            ],
            "additive_codes_found": ["330"],
            "review_required": False,
            "disclaimer": "Identification only.",
        },
    )

    response = client.post(
        "/api/v1/analyze/image",
        files={
            "file": ("label.png", b"fake image", "image/png")
        },
    )

    assert response.status_code == 200

    data = response.json()
    additive = data["additives"][0]

    assert additive["code"] == "330"
    assert additive["evidence"]["name"] == "Citric acid"
    assert "fssai" in additive["evidence"]["sources"]
    assert "jecfa" in additive["evidence"]["sources"]
    assert additive["safety_conclusion"] is None


def test_analyze_empty_text_raises_422(monkeypatch):
    monkeypatch.setattr(
        analyze_api,
        "extract_text",
        lambda image_bytes: {
            "extracted_text": "   ",
            "character_count": 0,
            "has_text": False,
        },
    )

    response = client.post(
        "/api/v1/analyze/image",
        files={
            "file": ("empty.png", b"fake image", "image/png")
        },
    )
    assert response.status_code == 422
    assert "No readable text" in response.json()["detail"]


def test_analyze_text_endpoint_with_nutrition():
    label_text = (
        "Ingredients: Whole wheat flour, sugar, palm oil, salt, acidity regulator (INS 330). "
        "Nutrition per 100g: Energy 450 kcal, Protein 7.5g, Carbohydrates 65g, "
        "Sugars 12g, Saturated Fat 3.5g, Salt 0.8g, Dietary Fibre 4.2g"
    )

    response = client.post(
        "/api/v1/analyze/text",
        json={"text": label_text, "product_name": "Test Cracker"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["ingredients"]) > 0
    assert any(a["code"] == "330" for a in data["additives"])
    assert data["nutrition"]["detected"] is True
    assert data["nutrition"]["nutrients"]["sugars_g"] == 12.0
    assert data["nutrition"]["nutrition_score"]["status"] == "scored"
    assert "not_calculable_from_label" in data["exposure"]["status"]
