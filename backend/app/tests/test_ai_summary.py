import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.ai_provider import (
    AITimeoutError,
    AIRateLimitError,
    AIAuthenticationError,
    MockAIProvider,
)
from app.services import ai_summary_service
from app.services.ai_summary_service import clear_summary_cache

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_cache():
    clear_summary_cache()
    yield
    clear_summary_cache()


SAMPLE_ANALYSIS_DATA = {
    "filename": "Sample Biscuit Label",
    "analysis_status": "completed",
    "ocr": {
        "extracted_text": "Ingredients: Wheat flour, sugar, palm oil, salt, INS 330, INS 500ii. Contains wheat.",
        "character_count": 82,
        "has_text": True,
    },
    "ingredients": [
        {"raw_text": "Wheat flour", "normalized_name": "Wheat flour", "recognized": True},
        {"raw_text": "sugar", "normalized_name": "Sugar", "recognized": True},
        {"raw_text": "palm oil", "normalized_name": "Palm oil", "recognized": True},
        {"raw_text": "salt", "normalized_name": "Salt", "recognized": True},
    ],
    "additives": [
        {
            "code": "330",
            "name": "Citric acid",
            "purpose": "Acidity regulator",
            "evidence_status": "verified_evidence",
            "evidence": {
                "name": "Citric acid",
                "adi": {"value": None, "status": "not_specified", "text": "Acceptable Daily Intake not specified (Safe at GMP)"},
                "scientific_findings": {
                    "summary": "Natural intermediate metabolite in carbohydrate metabolism.",
                    "acute_effects": None,
                    "chronic_effects": "No chronic toxicity or oncogenic hazard.",
                    "sensitivities": "High oral acidity may erode tooth enamel if unbuffered.",
                    "jecfa_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Chemical/1414",
                },
                "regulatory_details": {
                    "fssai_permitted": True,
                    "conditions": "Permitted across multiple food categories as per Good Manufacturing Practice (GMP).",
                    "source_url": "https://fssai.gov.in/",
                },
            },
        }
    ],
    "nutrition": {
        "detected": True,
        "nutrients": {
            "energy_kcal": 450.0,
            "sugars_g": 18.0,
            "saturated_fat_g": 4.5,
            "salt_g": 0.6,
        },
        "nutrition_score": {"score": 58, "status": "scored", "rating": "moderate"},
    },
    "exposure": {
        "status": "not_calculable_from_label",
        "explanation": "Packaged food labels list ingredients by weight but do not declare additive concentrations.",
    },
    "product": {
        "allergens": "Wheat",
    },
}


def test_deterministic_fallback_when_no_ai_key(monkeypatch):
    """When no AI provider is active, service returns grounded deterministic fallback."""
    monkeypatch.setattr(ai_summary_service, "get_ai_provider", lambda override=None: None)

    response = client.post(
        "/api/v1/analyze/ai-summary",
        json={
            "analysis_data": SAMPLE_ANALYSIS_DATA,
            "preferences": {
                "detail_level": "standard",
                "reading_level": "standard",
                "dietary_preferences": ["vegetarian"],
                "allergens_or_exclusions": ["palm oil", "peanuts"],
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["ai_enabled"] is False
    assert data["provider"] == "deterministic_grounded_fallback"
    assert "Live LLM summaries are disabled" in data["notice"]

    summary = data["summary"]
    assert "product_overview" in summary
    assert len(summary["ingredient_and_additive_explanations"]) >= 1
    assert summary["health_effects"]["long_term_effects"] is not None
    assert summary["exposure_assessment"]["status"] == "not_calculable_from_label"
    assert len(summary["source_references"]) >= 2
    assert "FSSAI" in summary["source_references"][1]["organization"]

    # Verify exclusions check
    alignments = summary["allergen_and_dietary_alignment"]
    palm_match = next((a for a in alignments if a["preference_or_allergen"] == "palm oil"), None)
    assert palm_match is not None
    assert palm_match["status"] == "contains_exclusion"

    peanuts_match = next((a for a in alignments if a["preference_or_allergen"] == "peanuts"), None)
    assert peanuts_match is not None
    assert peanuts_match["status"] == "matches"


def test_ai_summary_with_mock_provider(monkeypatch):
    """When a mock AI provider is returned, structured validation succeeds."""
    mock_response = {
        "product_overview": "A wheat cracker with standard ingredients and citric acid.",
        "nutritional_observations": ["Contains 18g sugars per 100g.", "Moderate fat content."],
        "ingredient_and_additive_explanations": [
            {
                "name": "INS 330 (Citric acid)",
                "purpose": "Acidity regulator",
                "scientific_findings": "Evaluated by JECFA with ADI not specified.",
                "evidence_status": "verified_evidence",
                "source_name": "WHO/FAO JECFA",
                "source_url": "https://apps.who.int/food-additives-contaminants-jecfa-database/",
            }
        ],
        "health_effects": {
            "short_term_effects": "No acute toxicity noted.",
            "long_term_effects": "No chronic toxicity at GMP levels.",
            "excessive_exposure_effects": "May cause mild gastric irritation if ingested in pure form.",
            "sensitivities_and_allergens": "Contains declared wheat.",
        },
        "exposure_assessment": {
            "status": "not_calculable_from_label",
            "explanation": "Exact additive concentration is not declared on retail package.",
            "reference_adi": "Not specified (Safe at GMP)",
        },
        "allergen_and_dietary_alignment": [
            {
                "preference_or_allergen": "vegetarian",
                "status": "matches",
                "explanation": "No animal ingredients declared.",
            }
        ],
        "missing_or_uncertain_information": ["Exact additive concentrations."],
        "consumer_next_steps": ["Review serving size.", "Check package allergen statement."],
        "source_references": [
            {
                "organization": "WHO/FAO JECFA",
                "title": "JECFA Database",
                "url": "https://apps.who.int/food-additives-contaminants-jecfa-database/",
            }
        ],
        "grounding_statement": "Grounding verified against JECFA monograph.",
    }

    mock_provider = MockAIProvider(mock_response=mock_response)
    monkeypatch.setattr(ai_summary_service, "get_ai_provider", lambda override=None: mock_provider)

    response = client.post(
        "/api/v1/analyze/ai-summary",
        json={"analysis_data": SAMPLE_ANALYSIS_DATA},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["ai_enabled"] is True
    assert data["provider"] == "mock"
    assert data["summary"]["product_overview"] == "A wheat cracker with standard ingredients and citric acid."


def test_ai_summary_caching(monkeypatch):
    """Calling AI summary twice with the same analysis payload yields cached result on second run."""
    monkeypatch.setattr(ai_summary_service, "get_ai_provider", lambda override=None: None)

    req_body = {"analysis_data": SAMPLE_ANALYSIS_DATA}
    res1 = client.post("/api/v1/analyze/ai-summary", json=req_body)
    assert res1.status_code == 200
    assert res1.json()["cached"] is False

    res2 = client.post("/api/v1/analyze/ai-summary", json=req_body)
    assert res2.status_code == 200
    assert res2.json()["cached"] is True


def test_ai_provider_timeout_graceful_fallback(monkeypatch):
    """When an AI provider times out, service falls back to deterministic summary with a warning."""
    class TimeoutProvider:
        provider_name = "timeout-sim"
        model_name = "timeout-v1"
        async def generate_json(self, prompt, system_instruction=None, timeout_seconds=10.0):
            raise AITimeoutError("Request to AI provider timed out after 10s")

    monkeypatch.setattr(ai_summary_service, "get_ai_provider", lambda override=None: TimeoutProvider())

    response = client.post(
        "/api/v1/analyze/ai-summary",
        json={"analysis_data": SAMPLE_ANALYSIS_DATA},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["ai_enabled"] is False
    assert data["provider"] == "deterministic_grounded_fallback"
    assert "AITimeoutError" in data.get("warning", "")


def test_ai_provider_validation_failure_fallback(monkeypatch):
    """When AI provider returns invalid schema, service gracefully falls back to deterministic summary."""
    class BadSchemaProvider:
        provider_name = "bad-schema-sim"
        model_name = "bad-v1"
        async def generate_json(self, prompt, system_instruction=None, timeout_seconds=10.0):
            # Missing mandatory fields required by StructuredProductSummary
            return {"unrelated_field": "hello world"}

    monkeypatch.setattr(ai_summary_service, "get_ai_provider", lambda override=None: BadSchemaProvider())

    response = client.post(
        "/api/v1/analyze/ai-summary",
        json={"analysis_data": SAMPLE_ANALYSIS_DATA},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["ai_enabled"] is False
    assert data["provider"] == "deterministic_grounded_fallback"
    assert "validation schema" in data.get("warning", "")
