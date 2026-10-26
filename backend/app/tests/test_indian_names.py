
from fastapi.testclient import TestClient

from app.main import app
from app.services.indian_name_service import resolve_indian_name
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


def test_recognizes_new_regional_aliases():
    assert resolve_indian_name("methi")["canonical_name"] == "fenugreek"
    assert resolve_indian_name("arisi")["canonical_name"] == "rice"
    assert resolve_indian_name("perungayam")["canonical_name"] == "asafoetida"


def test_recognizes_common_ingredient_descriptors():
    result = resolve_indian_name("organic haldi powder")

    assert result["matched"] is True
    assert result["canonical_name"] == "turmeric"
    assert result["status"] == "normalized_alias_match"


def test_does_not_guess_unknown_names():
    result = resolve_indian_name("xyzfoodingredient")

    assert result["matched"] is False
    assert result["canonical_name"] is None
    assert result["status"] == "needs_review"
