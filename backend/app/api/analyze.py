"""Combined food label intelligence and analysis router.

Orchestrates the complete pipeline:
Image Upload / Text Input -> OCR -> Ingredient Extraction -> Indian Alias
Resolution -> Additive Recognition -> Source-Backed Evidence Retrieval ->
Nutrition Parsing & Indicator Scoring -> Exposure Guidance -> Unified Output
-> Optional Evidence-Grounded AI Summary.
"""

import re
from typing import Any
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field, model_validator

from app.services.ocr_service import extract_text
from app.services.ingredient_service import analyze_ingredients
from app.services.evidence_service import get_additive_evidence
from app.services.indian_name_service import resolve_indian_name
from app.services.nutrition_score_service import calculate_nutrition_score
from app.services.ai_summary_service import (
    PersonalizationPreferences,
    generate_product_summary,
)

router = APIRouter(prefix="/analyze", tags=["Full Analysis"])


class TextAnalysisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50000, description="Raw or corrected label text to analyze.")
    product_name: str | None = Field(None, description="Optional product name for context.")


class AISummaryRequest(BaseModel):
    analysis_result: dict[str, Any] | None = Field(default=None, description="Full structured analysis payload.")
    analysis_data: dict[str, Any] | None = Field(default=None, description="Alternative alias for analysis_result.")
    preferences: PersonalizationPreferences | None = Field(default=None, description="Optional user personalization preferences.")
    provider_override: str | None = Field(default=None, description="Optional provider override ('gemini', 'mock', 'openai').")

    @model_validator(mode="after")
    def resolve_payload(self):
        if not self.analysis_result and not self.analysis_data:
            raise ValueError("Either analysis_result or analysis_data must be provided.")
        if not self.analysis_result:
            self.analysis_result = self.analysis_data
        return self


def _extract_nutrients_from_text(text: str) -> dict:
    """Heuristic extraction of nutritional values per 100g from OCR label text."""
    cleaned = text.lower()

    def find_num(pattern: str) -> float | None:
        match = re.search(pattern, cleaned)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, TypeError):
                return None
        return None

    energy = find_num(r"\benergy[^\d\n\r]*(\d+(?:\.\d+)?)\s*(?:kcal|cal|kj)")
    protein = find_num(r"\bprotein[s]?[^\d\n\r]*(\d+(?:\.\d+)?)\s*g")
    carbs = find_num(r"\bcarbohydrate[s]?[^\d\n\r]*(\d+(?:\.\d+)?)\s*g")
    sugar = find_num(r"\b(?:total\s+)?sugar[s]?[^\d\n\r]*(\d+(?:\.\d+)?)\s*g")
    fat = find_num(r"\b(?:total\s+)?fat[^\d\n\r]*(\d+(?:\.\d+)?)\s*g")
    sat_fat = find_num(r"\bsaturated\s+fat[^\d\n\r]*(\d+(?:\.\d+)?)\s*g")
    sodium = find_num(r"\bsodium[^\d\n\r]*(\d+(?:\.\d+)?)\s*(?:mg|g)")
    salt = find_num(r"\bsalt[^\d\n\r]*(\d+(?:\.\d+)?)\s*g")
    fiber = find_num(r"\b(?:dietary\s+)?fib[re]{2}[^\d\n\r]*(\d+(?:\.\d+)?)\s*g")

    # If sodium was found in mg and salt not found, estimate salt = sodium_mg * 2.5 / 1000
    if salt is None and sodium is not None:
        salt = round(sodium * 2.5 / 1000, 2)

    nutrients = {
        "energy_kcal": energy,
        "protein_g": protein,
        "carbohydrates_g": carbs,
        "sugars_g": sugar,
        "fat_g": fat,
        "saturated_fat_g": sat_fat,
        "sodium_mg": sodium,
        "salt_g": salt,
        "fiber_g": fiber,
    }

    has_any = any(v is not None for v in nutrients.values())

    score_input = {
        "sugars_100g": sugar,
        "saturated-fat_100g": sat_fat,
        "salt_100g": salt,
        "fiber_100g": fiber,
        "proteins_100g": protein,
    }
    nutrition_score = calculate_nutrition_score(score_input) if has_any else None

    return {
        "detected": has_any,
        "nutrients": nutrients,
        "nutrition_score": nutrition_score,
    }


def _process_analysis_pipeline(extracted_text: str, filename: str | None = None) -> dict:
    """Run stages 2 through 4 of the intelligence pipeline."""

    # Stage 2: Recognize ingredients and additive codes
    ingredient_result = analyze_ingredients(extracted_text)

    # Stage 2.5: Resolve ingredient names using the Indian alias dictionary
    for ingredient in ingredient_result.get("ingredients", []):
        original_name = ingredient.get("raw_text", "")
        normalized_name = ingredient.get("normalized_name", "")

        resolution = resolve_indian_name(original_name)
        if not resolution["matched"] and normalized_name:
            resolution = resolve_indian_name(normalized_name)

        ingredient["name_resolution"] = resolution

    # Stage 3: Attach source-linked evidence to each known additive
    enriched_additives = []
    for additive in ingredient_result.get("additives", []):
        evidence = get_additive_evidence(additive["code"])

        enriched_additives.append({
            **additive,
            "evidence_status": (
                evidence["evidence_status"]
                if evidence
                else "not_in_catalogue"
            ),
            "evidence": evidence,
        })

    ingredient_result["additives"] = enriched_additives

    # Stage 3.5: Extract nutrition info and compute score if present
    nutrition_data = _extract_nutrients_from_text(extracted_text)

    # Stage 3.6: Exposure guidance
    exposure_summary = {
        "status": "not_calculable_from_label",
        "reason": (
            "Packaged food labels list ingredients in descending order of weight, "
            "but do not disclose numeric additive concentrations (e.g. mg/kg). "
            "Use the Dietary Exposure Calculator tool with tested concentration or "
            "statutory maximum limits to evaluate acceptable daily intake."
        ),
        "additives_detected_count": len(enriched_additives),
        "additives_with_numeric_adi": [
            a["code"] for a in enriched_additives
            if a.get("evidence") and a["evidence"].get("adi", {}).get("status") == "numeric"
        ],
    }

    # Stage 4: Unified structured output
    return {
        "success": True,
        "filename": filename or "label_text_input",
        "analysis_status": (
            "review_required"
            if ingredient_result["review_required"]
            else "completed"
        ),
        "ocr": {
            "extracted_text": extracted_text,
            "character_count": len(extracted_text),
        },
        **ingredient_result,
        "nutrition": nutrition_data,
        "exposure": exposure_summary,
        "limitations": [
            "OCR can misread or omit micro-print label text. Review extracted text carefully.",
            "Ingredient recognition is matched against open reference lists and the Indian alias dictionary.",
            "Direct source links trace to WHO/FAO JECFA monographs and FSSAI schedules.",
            "Additive identification does not imply toxicity or personal health risk.",
            "Unrecognized terms require citizen-science human review.",
        ],
    }


@router.post("/image")
async def analyze_food_label(file: UploadFile = File(...)):
    """Extract label text, recognize ingredients and attach evidence from an uploaded image."""
    try:
        image_bytes = await file.read()

        # Stage 1: Extract text from the image
        ocr_result = extract_text(image_bytes)
        extracted_text = ocr_result["extracted_text"]

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text was detected. Try a clearer image "
                    "with good lighting and focused text on the ingredient label."
                ),
            )

        return _process_analysis_pipeline(extracted_text, filename=file.filename)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()


@router.post("/text")
def analyze_label_text(request: TextAnalysisRequest):
    """Analyze manually input or corrected OCR text directly."""
    try:
        return _process_analysis_pipeline(request.text, filename=request.product_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/ai-summary")
async def create_ai_summary(request: AISummaryRequest):
    """Generate a strictly evidence-grounded, personalized AI summary for an analyzed product."""
    try:
        return await generate_product_summary(
            analysis_data=request.analysis_result,
            preferences=request.preferences,
            provider_override=request.provider_override,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI summary: {exc}") from exc
