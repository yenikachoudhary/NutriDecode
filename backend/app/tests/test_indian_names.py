
from fastapi.testclient import TestClient

from app.main import app
from app.services.indian_name_service import resolve_indian_name

client = TestClient(app)


def test_resolves_hindi_turmeric_name():
    result = resolve_indian_name("haldi")

    assert result["matched"] is True
    assert result["canonical_name"] == "turmeric"
    assert result["status"] == "exact_dictionary_match"


def test_resolves_regional_salt_name():
    result = resolve_indian_name("uppu")

    assert result["matched"] is True
    assert result["canonical_name"] == "salt"


def test_unknown_name_is_not_guessed():
    result = resolve_indian_name("unknown ingredient xyz")

    assert result["matched"] is False
    assert result["canonical_name"] is None
    assert result["status"] == "needs_review"


def test_name_resolution_endpoint():
    response = client.get(
        "/api/v1/ingredients/resolve-name",
        params={"name": "haldi"},
    )

    assert response.status_code == 200
    assert response.json()["canonical_name"] == "turmeric"
