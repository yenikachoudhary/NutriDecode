
from math import isfinite
from typing import Any


# Prototype thresholds for packaged solid foods, measured per 100 g.
# These are transparent development rules, not an official scoring system.
THRESHOLDS = {
    "sugars_100g": {"low": 5.0, "high": 22.5, "max_penalty": 30},
    "saturated-fat_100g": {"low": 1.5, "high": 5.0, "max_penalty": 25},
    "salt_100g": {"low": 0.3, "high": 1.5, "max_penalty": 25},
}

CORE_NUTRIENTS = tuple(THRESHOLDS.keys())


def _read_value(nutrients: dict[str, Any], key: str) -> float | None:
    """Return a valid, non-negative numeric nutrient value, or None."""
    value = nutrients.get(key)

    if value is None or isinstance(value, bool):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not isfinite(number) or number < 0:
        return None

    return number


def _penalty(value: float, low: float, high: float, maximum: int) -> float:
    """Calculate a gradual penalty between the low and high thresholds."""
    if value <= low:
        return 0.0

    if value >= high:
        return float(maximum)

    return (value - low) / (high - low) * maximum


def calculate_nutrition_score(
    nutrients: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate an experimental nutrition indicator from values per 100 g.

    Required:
      sugars_100g
      saturated-fat_100g
      salt_100g

    Optional:
      fiber_100g
      proteins_100g

    Missing required values produce no overall score.
    """
    if not isinstance(nutrients, dict):
        raise ValueError("nutrients must be a dictionary")

    values = {
        key: _read_value(nutrients, key)
        for key in (*CORE_NUTRIENTS, "fiber_100g", "proteins_100g")
    }

    missing = [
        key for key in CORE_NUTRIENTS if values[key] is None
    ]

    if missing:
        return {
            "status": "insufficient_data",
            "score": None,
            "label": "Not enough nutrition data",
            "unit_basis": "per 100 g",
            "missing_nutrients": missing,
            "components": [],
            "methodology": (
                "An overall score requires sugar, saturated fat, "
                "and salt values per 100 g."
            ),
            "disclaimer": (
                "This prototype indicator is not an official nutrition "
                "rating, a medical assessment, or a food-safety verdict."
            ),
        }

    components = []
    total_penalty = 0.0
    total_bonus = 0.0

    for key, rule in THRESHOLDS.items():
        value = values[key]
        penalty = _penalty(
            value,
            rule["low"],
            rule["high"],
            rule["max_penalty"],
        )
        total_penalty += penalty

        components.append({
            "nutrient": key,
            "value_per_100g": value,
            "effect": "penalty",
            "points": round(penalty, 2),
            "explanation": (
                f"Values above {rule['low']} g/100 g increase the "
                f"penalty, up to {rule['max_penalty']} points at "
                f"{rule['high']} g/100 g."
            ),
        })

    # Optional positive indicators. Missing values are not treated as zero.
    for key, threshold, maximum in (
        ("fiber_100g", 3.0, 10),
        ("proteins_100g", 5.0, 10),
    ):
        value = values[key]

        if value is None:
            components.append({
                "nutrient": key,
                "value_per_100g": None,
                "effect": "not_scored",
                "points": 0,
                "explanation": "No value supplied; no bonus applied.",
            })
            continue

        bonus = min(maximum, max(0.0, (value - threshold) / threshold * 2 * maximum))
        total_bonus += bonus

        components.append({
            "nutrient": key,
            "value_per_100g": value,
            "effect": "bonus",
            "points": round(bonus, 2),
            "explanation": (
                f"A value above {threshold} g/100 g earns a capped "
                f"prototype bonus of {maximum} points."
            ),
        })

    score = round(max(0.0, min(100.0, 100 - total_penalty + total_bonus)))

    if score >= 75:
        label = "Higher indicator score"
    elif score >= 50:
        label = "Moderate indicator score"
    else:
        label = "Lower indicator score"

    return {
        "status": "scored",
        "score": score,
        "label": label,
        "unit_basis": "per 100 g",
        "missing_nutrients": [],
        "components": components,
        "calculation": {
            "starting_points": 100,
            "total_penalty": round(total_penalty, 2),
            "total_bonus": round(total_bonus, 2),
            "formula": (
                "Score = clamp(100 - penalties + optional bonuses, 0, 100)"
            ),
        },
        "methodology": (
            "Sugar, saturated fat, and salt contribute gradual penalties. "
            "Fibre and protein can contribute capped bonuses when values "
            "are available. The thresholds and weights are experimental."
        ),
        "disclaimer": (
            "This prototype indicator is not an official nutrition rating, "
            "a medical assessment, or a food-safety verdict. It does not "
            "account for serving size, the overall diet, or every nutritional "
            "factor. Compare products using their complete labels."
        ),
    }
