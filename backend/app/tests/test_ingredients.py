
from app.services.ingredient_service import analyze_ingredients


def test_extracts_known_additive_codes():
    result = analyze_ingredients(
        "Ingredients: Potato, Acidity Regulators (330, 296, 334), "
        "Anticaking Agent (551), Color (160c)"
    )

    assert set(result["additive_codes_found"]) == {
        "330", "296", "334", "551", "160c"
    }
    assert len(result["additives"]) == 5


def test_splits_grouped_oils():
    result = analyze_ingredients(
        "Ingredients: Edible Vegetable) (Palmolein, Rice Bran Oil)"
    )

    names = {
        item["normalized_name"] for item in result["ingredients"]
    }

    assert "edible vegetable" in names
    assert "palm olein" in names
    assert "rice bran oil" in names


def test_marks_unknown_terms_for_review():
    result = analyze_ingredients(
        "Ingredients: Potato, Unknown Ingredient XYZ"
    )

    unknown = next(
        item for item in result["ingredients"]
        if item["normalized_name"] == "unknown ingredient xyz"
    )

    assert unknown["recognized"] is False
    assert unknown["review_required"] is True
    assert result["review_required"] is True


def test_rejects_empty_text():
    try:
        analyze_ingredients(" ")
        assert False, "Expected ValueError for empty input"
    except ValueError:
        pass
