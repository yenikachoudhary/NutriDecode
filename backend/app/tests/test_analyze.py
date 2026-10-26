
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
