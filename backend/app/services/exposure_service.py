"""Dietary exposure calculation service.

Calculates estimated additive intake per serving, daily intake, and exposure
per kilogram of body weight, then compares it against an applicable ADI.
"""

from math import isfinite
from typing import Any
from app.services.evidence_service import ADDITIVE_EVIDENCE, get_additive_evidence


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

    Concentration must be in mg/kg of food matrix.
    ADI must be a verified, applicable reference value from an authoritative source (e.g. JECFA).
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
            "Estimated exposure is above the supplied ADI reference value. "
            "Review total cumulative dietary exposure, input assumptions, and applicable "
            "scientific guidance. This is not a diagnosis or proof of toxicity."
            if adi_percentage > 100
            else
            "Estimated exposure is at or below the supplied ADI reference value. "
            "This comparison alone does not establish that the entire product is safe "
            "or address other health or nutritional factors."
        ),
        "limitations": [
            "The concentration and ADI must be verified from authoritative, substance-specific sources.",
            "Packaged food labels generally do not declare precise additive concentrations; values must be tested or regulatory limits.",
            "Other dietary sources of the same additive may increase total daily exposure.",
            "An ADI comparison is a preliminary risk-characterisation tool, not a guarantee of safety or a medical diagnosis.",
        ],
    }


def get_reference_adi_for_additive(additive_code: str) -> dict | None:
    """Look up verified ADI details for an additive from the evidence database."""
    record = get_additive_evidence(additive_code)
    if not record:
        return None

    adi = record.get("adi", {})
    return {
        "code": record.get("code"),
        "name": record.get("name"),
        "ins_number": record.get("ins_number"),
        "adi_value_numeric": adi.get("value"),
        "adi_status": adi.get("status"),
        "adi_text": adi.get("text"),
        "unit": adi.get("unit"),
        "source": adi.get("evaluation_reference"),
        "is_calculable": adi.get("status") == "numeric",
        "note": (
            "Numeric ADI is available for exposure calculation."
            if adi.get("status") == "numeric"
            else "JECFA has designated this substance as 'ADI not specified', meaning toxicological testing established that intake under Good Manufacturing Practice does not represent a dietary hazard."
        ),
    }


def list_available_reference_adis() -> list[dict]:
    """List all additives in catalogue with ADI summary for calculator UI."""
    results = []
    for code in sorted(ADDITIVE_EVIDENCE.keys()):
        adi_info = get_reference_adi_for_additive(code)
        if adi_info:
            results.append(adi_info)
    return results
