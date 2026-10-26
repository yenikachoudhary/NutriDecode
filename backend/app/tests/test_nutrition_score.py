
from app.services.nutrition_score_service import calculate_nutrition_score


def test_complete_nutrition_data_returns_score():
    result = calculate_nutrition_score({
        "sugars_100g": 4,
        "saturated-fat_100g": 1,
        "salt_100g": 0.2,
        "fiber_100g": 5,
        "proteins_100g": 8,
    })

    assert result["status"] == "scored"
    assert isinstance(result["score"], int)
    assert 0 <= result["score"] <= 100
    assert len(result["components"]) == 5


def test_high_sugar_increases_penalty():
    lower_sugar = calculate_nutrition_score({
        "sugars_100g": 5,
        "saturated-fat_100g": 1,
        "salt_100g": 0.2,
    })
    higher_sugar = calculate_nutrition_score({
        "sugars_100g": 22.5,
        "saturated-fat_100g": 1,
        "salt_100g": 0.2,
    })

    assert higher_sugar["score"] < lower_sugar["score"]


def test_missing_required_nutrient_returns_no_score():
    result = calculate_nutrition_score({
        "sugars_100g": 10,
        "salt_100g": 0.5,
    })

    assert result["status"] == "insufficient_data"
    assert result["score"] is None
    assert "saturated-fat_100g" in result["missing_nutrients"]


def test_optional_nutrients_can_be_missing():
    result = calculate_nutrition_score({
        "sugars_100g": 10,
        "saturated-fat_100g": 2,
        "salt_100g": 0.5,
    })

    assert result["status"] == "scored"
    assert result["score"] is not None


def test_negative_nutrient_is_treated_as_missing():
    result = calculate_nutrition_score({
        "sugars_100g": -1,
        "saturated-fat_100g": 2,
        "salt_100g": 0.5,
    })

    assert result["status"] == "insufficient_data"
    assert result["score"] is None
