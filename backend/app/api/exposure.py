"""Dietary exposure calculation API router.

Allows users to calculate estimated additive intake and compare against
an authoritative Acceptable Daily Intake (ADI) reference value.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.exposure_service import (
    calculate_exposure,
    get_reference_adi_for_additive,
    list_available_reference_adis,
)

router = APIRouter(prefix="/exposure", tags=["Exposure Assessment"])


class ExposureCalculationRequest(BaseModel):
    concentration_mg_per_kg_food: float = Field(
        ...,
        ge=0,
        description="Declared concentration of additive in mg per kg of food matrix.",
    )
    serving_size_g: float = Field(
        ...,
        gt=0,
        description="Serving size consumed in grams.",
    )
    body_weight_kg: float = Field(
        ...,
        gt=0,
        description="Consumer body weight in kilograms.",
    )
    adi_mg_per_kg_body_weight_day: float = Field(
        ...,
        gt=0,
        description="Acceptable Daily Intake (ADI) reference value in mg/kg body weight/day.",
    )
    servings_per_day: float = Field(
        1.0,
        gt=0,
        description="Number of servings consumed per day.",
    )
    additive_code: str | None = Field(
        None,
        description="Optional additive code for reference tracing.",
    )


@router.post("/calculate")
def compute_exposure(request: ExposureCalculationRequest):
    """Estimate daily additive exposure and compare with an applicable ADI."""
    try:
        result = calculate_exposure(
            concentration_mg_per_kg_food=request.concentration_mg_per_kg_food,
            serving_size_g=request.serving_size_g,
            body_weight_kg=request.body_weight_kg,
            adi_mg_per_kg_body_weight_day=request.adi_mg_per_kg_body_weight_day,
            servings_per_day=request.servings_per_day,
        )
        if request.additive_code:
            result["additive_code"] = request.additive_code
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/reference-adi/{code}")
def get_additive_adi(code: str):
    """Look up authoritative WHO/FAO JECFA reference ADI for an additive code."""
    adi_record = get_reference_adi_for_additive(code)
    if not adi_record:
        raise HTTPException(
            status_code=404,
            detail=f"No verified ADI record found for additive code '{code}'.",
        )
    return adi_record


@router.get("/reference-adis")
def list_reference_adis():
    """List all additives with documented ADI references for frontend selection."""
    return list_available_reference_adis()
