"""Unknown-Product Discovery Service for NutriDecode.

Provides candidate product search across registries when barcodes fail,
detects conflicting candidate records, estimates data completeness scores,
and flags unverified candidates without language-model hallucination.
"""

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from app.services.product_service import USER_AGENT

logger = logging.getLogger(__name__)

OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"


def calculate_data_completeness(product: dict[str, Any]) -> int:
    """Calculate a data completeness percentage (0-100) for a product record."""
    score = 0
    # Identity (30 points)
    if product.get("name") or product.get("product_name"):
        score += 15
    if product.get("brands"):
        score += 15

    # Visual (10 points)
    if product.get("front_image_url") or product.get("image_front_url"):
        score += 10

    # Ingredients (35 points)
    if product.get("ingredients_text") or product.get("ingredients_text_en"):
        score += 35

    # Nutrition (25 points)
    nutriments = product.get("nutriments") or product.get("nutrition_per_100g") or {}
    nutri_points = 0
    for key in ("energy_kcal", "sugars_g", "salt_g", "energy-kcal_100g", "sugars_100g", "salt_100g"):
        if nutriments.get(key) is not None:
            nutri_points += 8
    score += min(25, nutri_points)

    return min(100, score)


def detect_record_conflicts(candidates: list[dict[str, Any]]) -> list[str]:
    """Identify conflicting formulations or divergent brands among candidate records."""
    conflicts = []
    if len(candidates) < 2:
        return conflicts

    brands = {c.get("brands", "").lower().strip() for c in candidates if c.get("brands")}
    if len(brands) > 1:
        conflicts.append(f"Multiple differing brands found matching this search: {', '.join(sorted(brands))}.")

    # Check for ingredient discrepancies
    ing_texts = [c.get("ingredients_snippet") for c in candidates if c.get("ingredients_snippet")]
    if len(ing_texts) >= 2 and len(set(ing_texts)) > 1:
        conflicts.append("Differing ingredient formulations detected between package variants.")

    return conflicts


async def search_candidate_products(
    query: str,
    client: httpx.AsyncClient | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """Search Open Food Facts for candidate product matches when barcode is absent or not found."""
    cleaned_query = query.strip()
    if not cleaned_query:
        return {
            "query": query,
            "candidates_found": 0,
            "candidates": [],
            "conflicts_detected": [],
            "message": "Please provide a product title or keyword to search.",
        }

    params = {
        "search_terms": cleaned_query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit,
        "fields": (
            "code,product_name,brands,quantity,image_front_url,"
            "ingredients_text,nutriments,nutrition_grades"
        ),
    }

    retrieval_time = datetime.now(timezone.utc).isoformat()

    async def _fetch(c: httpx.AsyncClient):
        response = await c.get(
            OFF_SEARCH_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

    try:
        if client:
            payload = await _fetch(client)
        else:
            async with httpx.AsyncClient(timeout=10.0) as temp_client:
                payload = await _fetch(temp_client)

        raw_products = payload.get("products") or []
        candidates = []

        for p in raw_products:
            ing_text = p.get("ingredients_text") or ""
            snippet = ing_text[:160] + "..." if len(ing_text) > 160 else ing_text
            completeness = calculate_data_completeness(p)

            candidates.append({
                "barcode": p.get("code") or "N/A",
                "name": p.get("product_name") or "Unnamed Product",
                "brands": p.get("brands") or "Unknown Brand",
                "quantity": p.get("quantity"),
                "image_url": p.get("image_front_url"),
                "ingredients_snippet": snippet or "No ingredient text in database",
                "has_ingredients": bool(ing_text),
                "data_completeness_percent": completeness,
                "nutrition_grade": p.get("nutrition_grades"),
                "is_verified_match": False,  # Explicitly unverified candidate
                "source": "Open Food Facts Registry Search",
                "retrieval_timestamp": retrieval_time,
                "action_prompt": (
                    "Unverified candidate record. Verify barcode or upload package photograph."
                    if completeness < 75
                    else "Candidate record found. Cross-check with physical package."
                ),
            })

        conflicts = detect_record_conflicts(candidates)

        return {
            "query": cleaned_query,
            "candidates_found": len(candidates),
            "candidates": candidates,
            "conflicts_detected": conflicts,
            "retrieval_timestamp": retrieval_time,
            "message": (
                f"Found {len(candidates)} candidate product record(s). "
                "These are unverified candidates; verify against physical packaging."
                if candidates
                else "No matching products found in the public database. Upload a label photo instead."
            ),
        }

    except Exception as exc:
        logger.warning("Product discovery search failed for '%s': %s", cleaned_query, exc)
        return {
            "query": cleaned_query,
            "candidates_found": 0,
            "candidates": [],
            "conflicts_detected": [],
            "error": str(exc),
            "message": "Product discovery search was unable to reach the registry. Upload a label photo instead.",
        }


def get_additive_discovery_guidance(additive_code: str, evidence: dict[str, Any] | None) -> dict[str, Any]:
    """Provide discovery guidance for unknown or uncatalogued additives in Exposure Calculator."""
    code_cleaned = additive_code.lower().replace("ins", "").replace("e", "").strip()

    if evidence and evidence.get("adi", {}).get("status") == "numeric":
        adi_val = evidence["adi"]["value"]
        return {
            "code": code_cleaned,
            "has_numeric_adi": True,
            "reference_adi": f"{adi_val} mg/kg bw/day",
            "guidance_type": "verified_adi_available",
            "recommendation": f"Verified JECFA ADI of {adi_val} mg/kg bw/day is loaded. You can directly calculate exposure.",
        }

    if evidence and evidence.get("adi", {}).get("status") in ("not_specified", "not_limited"):
        return {
            "code": code_cleaned,
            "has_numeric_adi": False,
            "reference_adi": "Not specified (Safe at GMP)",
            "guidance_type": "gmp_additive",
            "recommendation": (
                "JECFA evaluated this substance and determined that numeric limitation is unnecessary "
                "when used within Good Manufacturing Practice (GMP). Exposure assessment does not require numeric ADI comparison."
            ),
            "fssai_guidance": "Permitted across standard categories under FSSAI schedule Appendix A.",
        }

    return {
        "code": code_cleaned,
        "has_numeric_adi": False,
        "reference_adi": "Unverified or not in catalogue",
        "guidance_type": "uncatalogued_additive",
        "recommendation": (
            f"Additive code '{additive_code}' does not have an established local catalogue record. "
            "Check official FSSAI regulation Appendix A for category-specific Maximum Permitted Levels (MPL)."
        ),
        "source_search_url": f"https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Search?search={code_cleaned}",
    }
