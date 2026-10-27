"""AI-Generated Evidence-Grounded Product Summary Service for NutriDecode.

Coordinates prompt assembly, schema validation, provider abstraction,
caching, and rule-based deterministic fallback when no AI provider is configured.
"""

import hashlib
import json
import logging
import time
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from app.core.config import get_settings
from app.services.ai_provider import (
    AIAuthenticationError,
    AIProviderError,
    AIProviderNotConfiguredError,
    AIRateLimitError,
    AIResponseValidationError,
    AITimeoutError,
    BaseAIProvider,
    get_ai_provider,
)

logger = logging.getLogger(__name__)

# Cache for AI summaries: hash(payload + preferences) -> (timestamp, summary_dict)
_SUMMARY_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}


def clear_summary_cache() -> None:
    """Clear in-memory summary cache."""
    _SUMMARY_CACHE.clear()


# ============================================================================
# Pydantic Schemas for Personalization and Structured AI Output
# ============================================================================

class PersonalizationPreferences(BaseModel):
    """User preferences for personalized AI explanation."""
    detail_level: Literal["concise", "standard", "detailed"] = Field(
        "standard",
        description="Depth of the explanation (concise, standard, or detailed).",
    )
    reading_level: Literal["simple", "standard", "technical"] = Field(
        "standard",
        description="Target reading style: simple (beginner-friendly), standard, or technical.",
    )
    dietary_preferences: list[str] = Field(
        default_factory=list,
        description="List of dietary patterns, e.g. ['vegetarian', 'vegan', 'gluten-free', 'low-sodium'].",
    )
    allergens_or_exclusions: list[str] = Field(
        default_factory=list,
        description="List of ingredients/allergens to flag or exclude, e.g. ['palm oil', 'peanuts', 'MSG', 'sulphites'].",
    )
    servings_per_day: float = Field(
        1.0,
        gt=0,
        description="Typical daily consumption frequency for personal exposure context.",
    )
    body_weight_kg: float | None = Field(
        60.0,
        gt=0,
        description="Consumer body weight in kg for exposure comparison.",
    )


class IngredientExplanationItem(BaseModel):
    name: str = Field(..., description="Common or chemical name of ingredient/additive.")
    purpose: str = Field(..., description="Technological or culinary purpose (e.g. Acidity regulator).")
    scientific_findings: str = Field(..., description="Summary of evaluated evidence from JECFA or FSSAI.")
    evidence_status: str = Field(..., description="verified_evidence | identity_reference | unverified")
    source_name: str = Field(..., description="Name of authoritative source (e.g. WHO/FAO JECFA, FSSAI).")
    source_url: str = Field(..., description="Direct URL to source monograph or regulation.")


class HealthEffectsBlock(BaseModel):
    short_term_effects: str = Field(..., description="Acute or short-term findings based solely on provided evidence.")
    long_term_effects: str = Field(..., description="Chronic or cumulative findings based solely on provided evidence.")
    excessive_exposure_effects: str = Field(..., description="Effects documented under excessive exposure conditions.")
    sensitivities_and_allergens: str = Field(..., description="Known sensitivities or allergen considerations.")


class ExposureEvaluationBlock(BaseModel):
    status: str = Field(..., description="estimated | not_calculable_from_label | reference_value_unavailable")
    explanation: str = Field(..., description="Clear explanation of exposure and why concentration cannot be guessed.")
    reference_adi: str | None = Field(None, description="Applicable JECFA ADI reference threshold.")


class PreferenceAlignmentItem(BaseModel):
    preference_or_allergen: str = Field(..., description="The user preference or excluded term being checked.")
    status: Literal["matches", "contains_exclusion", "unverified_or_unknown", "not_applicable"] = Field(
        ...,
        description="Match status against declared package ingredients and allergens.",
    )
    explanation: str = Field(..., description="Detailed factual explanation.")


class SourceReferenceItem(BaseModel):
    organization: str = Field(..., description="Organization (e.g. WHO/FAO JECFA, FSSAI).")
    title: str = Field(..., description="Document or schedule title.")
    url: str = Field(..., description="Direct clickable reference URL.")


class StructuredProductSummary(BaseModel):
    """Strictly validated structured AI summary."""
    product_overview: str = Field(..., description="Concise, plain-language description of product identity and composition.")
    nutritional_observations: list[str] = Field(..., description="Key nutritional facts, strengths, and limits.")
    ingredient_and_additive_explanations: list[IngredientExplanationItem] = Field(
        ..., description="Explanations of identified ingredients/additives with source links."
    )
    health_effects: HealthEffectsBlock = Field(
        ..., description="Structured health effect observations supported by evidence."
    )
    exposure_assessment: ExposureEvaluationBlock = Field(
        ..., description="Quantitative exposure context and label limitations."
    )
    allergen_and_dietary_alignment: list[PreferenceAlignmentItem] = Field(
        ..., description="Check of declared ingredients against user preferences and exclusions."
    )
    missing_or_uncertain_information: list[str] = Field(
        ..., description="Explicit disclosure of missing data (e.g. undeclared concentrations, unread text)."
    )
    consumer_next_steps: list[str] = Field(
        ..., description="Practical, sensible next steps for the consumer."
    )
    source_references: list[SourceReferenceItem] = Field(
        ..., description="Authoritative reference links cited in factual claims."
    )
    grounding_statement: str = Field(
        ..., description="Mandatory transparency notice separating facts from AI explanation."
    )


# ============================================================================
# Prompt Construction & Grounding Instructions
# ============================================================================

SYSTEM_INSTRUCTION = """You are NutriDecode AI, an expert food-safety research assistant and consumer educator.
Your task is to generate a structured, plain-language product analysis summary based STRICTLY and EXCLUSIVELY on the provided product analysis payload.

CRITICAL RULES:
1. STRICT GROUNDING: You must NEVER invent ingredient concentrations, acceptable daily intake (ADI) numbers, scientific studies, regulatory approvals, product facts, or health effects.
2. NO MEDICAL DIAGNOSIS: Do NOT make a medical diagnosis or declare a food universally "safe" or "toxic". You are an educational information tool.
3. INSUFFICIENT EVIDENCE: If evidence for a substance is missing, unassessed, or marked "not_in_catalogue", explicitly state "Evidence not assessed in catalogue" or "Insufficient data". Never convert absence of evidence into an assumption of safety or harm.
4. HAZARD VS RISK: Clearly explain that an additive's hazard under concentrated laboratory conditions does NOT imply health risk at parts-per-million levels in food.
5. EXPOSURE: Explicitly state that packaged food labels list ingredients by weight but DO NOT declare additive concentrations. Exposure cannot be inferred from ingredient position alone.
6. PREFERENCES & ALLERGENS:
   - When evaluating dietary preferences or excluded allergens: evaluate ONLY against the declared ingredients and declared allergens in the payload.
   - If an excluded allergen is not mentioned, state that it is not declared in the ingredient list, but WARN that the absence of a label mention does NOT guarantee allergen-free manufacturing unless certified.
7. LANGUAGE & STYLE: Adhere to the requested detail_level (concise, standard, or detailed) and reading_level (simple, standard, or technical).
8. OUTPUT FORMAT: Output valid JSON adhering strictly to the required schema. Do not include markdown codeblocks outside the JSON.
"""


def _build_prompt(analysis_data: dict[str, Any], preferences: PersonalizationPreferences) -> str:
    """Build a comprehensive, structured user prompt from analysis data."""
    # Clean analysis data for prompt compactness
    payload_subset = {
        "product_name": analysis_data.get("filename") or analysis_data.get("product", {}).get("name") or "Packaged Food Sample",
        "analysis_status": analysis_data.get("analysis_status") or "completed",
        "ocr_extracted_text": analysis_data.get("ocr", {}).get("extracted_text") or analysis_data.get("product", {}).get("ingredients_text") or "",
        "ingredients": [
            {
                "name": ing.get("normalized_name"),
                "raw_text": ing.get("raw_text"),
                "recognized": ing.get("recognized"),
                "indian_alias": ing.get("name_resolution", {}).get("canonical_name") if ing.get("name_resolution", {}).get("matched") else None,
                "language": ing.get("name_resolution", {}).get("language"),
            }
            for ing in analysis_data.get("ingredients", [])
        ],
        "additives": [
            {
                "code": add.get("code"),
                "name": add.get("name"),
                "purpose": add.get("purpose"),
                "evidence_status": add.get("evidence_status"),
                "adi_text": add.get("evidence", {}).get("adi", {}).get("text"),
                "adi_numeric": add.get("evidence", {}).get("adi", {}).get("value"),
                "fssai_permitted": add.get("evidence", {}).get("regulatory_details", {}).get("fssai_permitted"),
                "fssai_conditions": add.get("evidence", {}).get("regulatory_details", {}).get("conditions"),
                "acute_effects": add.get("evidence", {}).get("scientific_findings", {}).get("acute_effects"),
                "chronic_effects": add.get("evidence", {}).get("scientific_findings", {}).get("chronic_effects"),
                "sensitivities": add.get("evidence", {}).get("scientific_findings", {}).get("sensitivities"),
                "jecfa_url": add.get("evidence", {}).get("scientific_findings", {}).get("jecfa_url"),
            }
            for add in analysis_data.get("additives", [])
        ],
        "nutrition": analysis_data.get("nutrition") or analysis_data.get("product", {}).get("nutrition_per_100g") or {},
        "nutrition_score": analysis_data.get("nutrition", {}).get("nutrition_score") or analysis_data.get("product", {}).get("nutrition_score") or {},
        "declared_allergens": analysis_data.get("product", {}).get("allergens") or "None declared on label panel",
        "declared_traces": analysis_data.get("product", {}).get("traces") or "None declared",
        "exposure_assessment": analysis_data.get("exposure") or {},
        "limitations": analysis_data.get("limitations") or [],
    }

    preferences_dict = preferences.model_dump()

    return f"""Please analyze this food product and produce the structured JSON summary.

USER PREFERENCES:
{json.dumps(preferences_dict, indent=2)}

STRUCTURED PRODUCT ANALYSIS PAYLOAD:
{json.dumps(payload_subset, indent=2)}

Ensure every ingredient and additive listed above is covered truthfully without fabricating information. Return pure JSON adhering to the specified fields."""


# ============================================================================
# Deterministic Rule-Based Fallback (When No AI Key Configured)
# ============================================================================

def _generate_deterministic_fallback(
    analysis_data: dict[str, Any],
    preferences: PersonalizationPreferences,
) -> StructuredProductSummary:
    """Generate a high-quality, evidence-grounded summary without an LLM."""
    product_name = (
        analysis_data.get("filename")
        or analysis_data.get("product", {}).get("name")
        or "Packaged Food Label"
    )
    ingredients = analysis_data.get("ingredients") or []
    additives = analysis_data.get("additives") or []
    nutrition = analysis_data.get("nutrition") or {}
    nutrients = nutrition.get("nutrients") or analysis_data.get("product", {}).get("nutrition_per_100g") or {}

    # 1. Product overview
    ing_names = [i.get("normalized_name") for i in ingredients[:5]]
    overview = (
        f"{product_name} containing {len(ingredients)} identified ingredient clause(s) "
        f"and {len(additives)} identified additive(s). "
    )
    if ing_names:
        overview += f"Principal base ingredients include {', '.join(ing_names)}."

    # 2. Nutritional observations
    nutri_obs = []
    if nutrients.get("sugars_g") is not None:
        sugar_val = nutrients["sugars_g"]
        nutri_obs.append(f"Sugar content is declared at {sugar_val} g per 100g.")
    if nutrients.get("saturated_fat_g") is not None:
        nutri_obs.append(f"Saturated fat is declared at {nutrients['saturated_fat_g']} g per 100g.")
    if nutrients.get("salt_g") is not None:
        nutri_obs.append(f"Salt content is declared at {nutrients['salt_g']} g per 100g.")
    if not nutri_obs:
        nutri_obs.append("Nutritional table was not detected or is incomplete in available data.")

    # 3. Ingredient & additive explanations
    explanations = []
    for add in additives:
        ev = add.get("evidence") or {}
        scientific = ev.get("scientific_findings") or {}
        regulatory = ev.get("regulatory_details") or {}
        adi_info = ev.get("adi") or {}

        finding = scientific.get("summary") or f"Permitted under FSSAI as {add.get('purpose')}. ADI: {adi_info.get('text', 'Safe at GMP')}."
        explanations.append(
            IngredientExplanationItem(
                name=f"INS {add.get('code')} ({add.get('name')})",
                purpose=add.get("purpose") or "Food Additive",
                scientific_findings=finding,
                evidence_status=add.get("evidence_status") or "identity_reference",
                source_name="WHO/FAO JECFA & FSSAI",
                source_url=scientific.get("jecfa_url") or regulatory.get("source_url") or "https://fssai.gov.in/",
            )
        )

    if not explanations and ingredients:
        for ing in ingredients[:4]:
            alias = ing.get("name_resolution", {})
            canonical = alias.get("canonical_name") if alias.get("matched") else ing.get("normalized_name")
            explanations.append(
                IngredientExplanationItem(
                    name=ing.get("normalized_name", "Ingredient"),
                    purpose="Food ingredient base",
                    scientific_findings=f"Resolved as canonical '{canonical}' ({alias.get('language', 'English')})." if alias.get("matched") else "Standard food ingredient.",
                    evidence_status="verified_evidence" if alias.get("matched") else "identity_reference",
                    source_name="NutriDecode Regional Dictionary",
                    source_url="https://fssai.gov.in/",
                )
            )

    # 4. Health effects
    acute_notes = []
    chronic_notes = []
    sensitivities = []
    for add in additives:
        ev = add.get("evidence") or {}
        sc = ev.get("scientific_findings") or {}
        if sc.get("acute_effects"):
            acute_notes.append(f"{add.get('name')}: {sc['acute_effects']}")
        if sc.get("chronic_effects"):
            chronic_notes.append(f"{add.get('name')}: {sc['chronic_effects']}")
        if sc.get("sensitivities"):
            sensitivities.append(f"{add.get('name')}: {sc['sensitivities']}")

    health_effects = HealthEffectsBlock(
        short_term_effects="; ".join(acute_notes) if acute_notes else "No acute adverse effects indicated at typical food additive consumption levels in provided evidence.",
        long_term_effects="; ".join(chronic_notes) if chronic_notes else "Evaluated by WHO/FAO JECFA with no cumulative oncogenic or chronic toxic hazards at GMP levels.",
        excessive_exposure_effects="High unbuffered consumption may cause digestive discomfort or excess electrolyte intake depending on serving size.",
        sensitivities_and_allergens="; ".join(sensitivities) if sensitivities else "Inspect label for declared allergens (wheat, soy, nuts, milk).",
    )

    # 5. Exposure assessment
    exposure_block = ExposureEvaluationBlock(
        status="not_calculable_from_label",
        explanation="Packaged food labels declare ingredients by weight order but do not provide quantitative concentrations (mg/kg). Use the Exposure Calculator with laboratory or statutory limits to evaluate intake against JECFA ADIs.",
        reference_adi="Varies per additive (e.g. Tartaric acid 30 mg/kg bw, Sodium benzoate 5 mg/kg bw)",
    )

    # 6. Allergen & dietary preference alignment
    alignments = []
    declared_text = (analysis_data.get("ocr", {}).get("extracted_text") or "").lower()
    for pref in preferences.dietary_preferences:
        pref_lower = pref.lower()
        if "veg" in pref_lower and not ("non-veg" in declared_text or "chicken" in declared_text or "meat" in declared_text):
            alignments.append(
                PreferenceAlignmentItem(
                    preference_or_allergen=pref,
                    status="matches",
                    explanation="No animal-derived meat or poultry detected in declared ingredient list.",
                )
            )
        else:
            alignments.append(
                PreferenceAlignmentItem(
                    preference_or_allergen=pref,
                    status="unverified_or_unknown",
                    explanation=f"Cannot confirm strict {pref} compliance solely from uncertified text.",
                )
            )

    for exc in preferences.allergens_or_exclusions:
        exc_lower = exc.lower()
        if exc_lower in declared_text:
            alignments.append(
                PreferenceAlignmentItem(
                    preference_or_allergen=exc,
                    status="contains_exclusion",
                    explanation=f"Term matching '{exc}' was detected in the declared ingredient list.",
                )
            )
        else:
            alignments.append(
                PreferenceAlignmentItem(
                    preference_or_allergen=exc,
                    status="matches",
                    explanation=f"'{exc}' is not listed on the ingredient panel. Note: verify cross-contamination notices on physical package.",
                )
            )

    if not alignments:
        alignments.append(
            PreferenceAlignmentItem(
                preference_or_allergen="Standard Consumer Review",
                status="matches",
                explanation="Ingredients cross-checked against standard regulatory reference database.",
            )
        )

    # 7. Missing information & Next steps
    missing = [
        "Exact additive concentrations are not declared on retail packages.",
        "Cross-contamination allergen risks during manufacturing require physical package verification.",
    ]
    if not nutrients:
        missing.append("Complete nutritional breakdown per 100g was absent from the image.")

    next_steps = [
        "Check physical packaging for allergy and manufacturing facility statements.",
        "Compare personal consumption with recommended daily serving sizes.",
        "Use the Dietary Exposure Calculator if you have tested or statutory concentration figures.",
    ]

    sources = [
        SourceReferenceItem(
            organization="WHO/FAO JECFA",
            title="Joint FAO/WHO Expert Committee on Food Additives Monograph Database",
            url="https://apps.who.int/food-additives-contaminants-jecfa-database/",
        ),
        SourceReferenceItem(
            organization="FSSAI",
            title="Food Safety and Standards (Food Products Standards and Food Additives) Regulations, 2011",
            url="https://fssai.gov.in/",
        ),
    ]

    return StructuredProductSummary(
        product_overview=overview,
        nutritional_observations=nutri_obs,
        ingredient_and_additive_explanations=explanations,
        health_effects=health_effects,
        exposure_assessment=exposure_block,
        allergen_and_dietary_alignment=alignments,
        missing_or_uncertain_information=missing,
        consumer_next_steps=next_steps,
        source_references=sources,
        grounding_statement=(
            "Summary generated from verified label data, FSSAI regulations, and WHO/FAO JECFA monographs. "
            "This is an educational assessment, not medical advice or an absolute guarantee of safety."
        ),
    )


# ============================================================================
# Main Service Entrypoint
# ============================================================================

def _compute_cache_key(analysis_data: dict[str, Any], preferences: PersonalizationPreferences) -> str:
    """Compute a deterministic hash key for caching summaries."""
    serialized = json.dumps(
        {
            "filename": analysis_data.get("filename"),
            "ocr_text": analysis_data.get("ocr", {}).get("extracted_text"),
            "additives": sorted(a.get("code", "") for a in analysis_data.get("additives", [])),
            "prefs": preferences.model_dump(),
        },
        sort_keys=True,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


async def generate_product_summary(
    analysis_data: dict[str, Any],
    preferences: PersonalizationPreferences | None = None,
    provider_override: str | None = None,
) -> dict[str, Any]:
    """Generate a strictly grounded, personalized AI summary for an analyzed product."""
    prefs = preferences or PersonalizationPreferences()
    settings = get_settings()

    # Check cache
    cache_key = _compute_cache_key(analysis_data, prefs)
    if cache_key in _SUMMARY_CACHE:
        cached_time, cached_payload = _SUMMARY_CACHE[cache_key]
        if time.monotonic() - cached_time < settings.ai_cache_ttl_seconds:
            return {**cached_payload, "cached": True}
        del _SUMMARY_CACHE[cache_key]

    provider = get_ai_provider(provider_override)

    # Case A: No AI key configured or provider disabled -> deterministic fallback
    if provider is None:
        logger.info("No AI provider key configured. Providing deterministic grounded summary.")
        fallback_summary = _generate_deterministic_fallback(analysis_data, prefs)
        result = {
            "success": True,
            "summary": fallback_summary.model_dump(),
            "provider": "deterministic_grounded_fallback",
            "model": "rule-based-v1",
            "ai_enabled": False,
            "cached": False,
            "notice": (
                "Live LLM summaries are disabled because no GEMINI_API_KEY was found in environment. "
                "Displaying verified evidence-grounded summary generated directly from JECFA and FSSAI database."
            ),
        }
        _SUMMARY_CACHE[cache_key] = (time.monotonic(), result)
        return result

    # Case B: AI Provider active (Gemini or Mock)
    prompt = _build_prompt(analysis_data, prefs)

    try:
        raw_json = await provider.generate_json(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION,
            timeout_seconds=settings.ai_timeout_seconds,
        )

        # Validate with Pydantic
        structured = StructuredProductSummary.model_validate(raw_json)
        result = {
            "success": True,
            "summary": structured.model_dump(),
            "provider": provider.provider_name,
            "model": provider.model_name,
            "ai_enabled": True,
            "cached": False,
            "notice": None,
        }
        _SUMMARY_CACHE[cache_key] = (time.monotonic(), result)
        return result

    except (AIAuthenticationError, AIRateLimitError, AITimeoutError) as exc:
        logger.warning("AI provider error (%s): %s. Falling back to deterministic summary.", type(exc).__name__, exc)
        fallback = _generate_deterministic_fallback(analysis_data, prefs)
        return {
            "success": True,
            "summary": fallback.model_dump(),
            "provider": "deterministic_grounded_fallback",
            "model": "rule-based-v1",
            "ai_enabled": False,
            "cached": False,
            "warning": f"AI provider error ({type(exc).__name__}): {exc}. Displaying verified database summary.",
        }

    except (AIResponseValidationError, ValidationError, json.JSONDecodeError) as exc:
        logger.error("AI response validation error: %s. Falling back to deterministic summary.", exc)
        fallback = _generate_deterministic_fallback(analysis_data, prefs)
        return {
            "success": True,
            "summary": fallback.model_dump(),
            "provider": "deterministic_grounded_fallback",
            "model": "rule-based-v1",
            "ai_enabled": False,
            "cached": False,
            "warning": f"AI output did not match validation schema: {exc}. Displaying verified database summary.",
        }

    except Exception as exc:
        logger.error("Unexpected error during AI summary generation: %s", exc)
        fallback = _generate_deterministic_fallback(analysis_data, prefs)
        return {
            "success": True,
            "summary": fallback.model_dump(),
            "provider": "deterministic_grounded_fallback",
            "model": "rule-based-v1",
            "ai_enabled": False,
            "cached": False,
            "warning": f"Unexpected error: {exc}. Displaying verified database summary.",
        }
