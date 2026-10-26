
from math import isfinite
from typing import Any


def _positive_number(value: Any, field: str, *, allow_zero: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a valid number.")

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be a valid number.") from None

    if not isfinite(number):
        raise ValueError(f"{field} must be finite.")

    if number < 0 or (number == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "greater than zero"
        raise ValueError(f"{field} must be {qualifier}.")

    return number


def calculate_exposure(
    concentration_mg_per_kg_food: Any,
    serving_size_g: Any,
    body_weight_kg: Any,
    adi_mg_per_kg_body_weight_day: Any,
    servings_per_day: Any = 1,
) -> dict:
    """Estimate additive exposure and compare it with a supplied ADI.

    Concentration must be in mg/kg of food.
    ADI must be a verified, applicable reference value from a reliable source.
    """

    concentration = _positive_number(
        concentration_mg_per_kg_food, "concentration", allow_zero=True
    )
    serving = _positive_number(serving_size_g, "serving_size_g")
    weight = _positive_number(body_weight_kg, "body_weight_kg")
    adi = _positive_number(
        adi_mg_per_kg_body_weight_day, "ADI"
    )
    frequency = _positive_number(servings_per_day, "servings_per_day")

    intake_mg_day = concentration * (serving / 1000) * frequency
    exposure = intake_mg_day / weight
    adi_percentage = (exposure / adi) * 100

    return {
        "status": "estimated",
        "concentration_mg_per_kg_food": concentration,
        "serving_size_g": serving,
        "servings_per_day": frequency,
        "body_weight_kg": weight,
        "estimated_intake_mg_per_day": round(intake_mg_day, 6),
        "estimated_exposure_mg_per_kg_body_weight_day": round(exposure, 6),
        "adi_mg_per_kg_body_weight_day": adi,
        "adi_percentage": round(adi_percentage, 2),
        "interpretation": (
            "Estimated exposure is above the supplied ADI reference. "
            "Review total dietary exposure, assumptions, and the applicable "
            "scientific guidance."
            if adi_percentage > 100
            else
            "Estimated exposure is at or below the supplied ADI reference. "
            "This comparison alone does not establish that the product is "
            "safe or assess other hazards."
        ),
        "limitations": [
            "The concentration and ADI must be verified from reliable sources.",
            "Other dietary sources may increase total exposure.",
            "The result depends on the serving size and consumption frequency.",
            "An ADI comparison is not a guarantee of safety or a medical diagnosis.",
        ],
    }
