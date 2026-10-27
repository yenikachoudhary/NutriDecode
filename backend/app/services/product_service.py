"""Product lookup service for packaged foods.

Queries Open Food Facts v2 API as the primary source, with UPCitemdb as
a fallback. Distinguishes genuine 404 not-found responses from external
provider downtime or rate limits, and caches successful lookups in memory.
"""

import logging
import re
import time
from typing import Any

import httpx
from app.services.nutrition_score_service import calculate_nutrition_score

logger = logging.getLogger(__name__)

OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v2/product"
USER_AGENT = "NutriDecode/0.1 (food-label research prototype; contact: info@nutridecode.local)"

REQUESTED_FIELDS = ",".join([
    "code",
    "product_name",
    "brands",
    "quantity",
    "countries",
    "ingredients_text",
    "ingredients_text_en",
    "allergens",
    "traces",
    "nutriments",
    "nutrition_grades",
    "nutriscore_grade",
    "nova_group",
    "additives_tags",
    "image_front_url",
    "url",
    "last_modified_t",
])

# In-memory cache for barcode lookups: barcode -> (timestamp, response_dict)
_BARCODE_CACHE: dict[str, tuple[float, dict]] = {}
CACHE_TTL_SECONDS = 900.0  # 15 minutes


def clear_cache() -> None:
    """Clear all in-memory product cache entries."""
    _BARCODE_CACHE.clear()


def _get_cached_product(barcode: str) -> dict | None:
    """Retrieve unexpired cached product data, if present."""
    if barcode in _BARCODE_CACHE:
        cached_time, data = _BARCODE_CACHE[barcode]
        if time.monotonic() - cached_time < CACHE_TTL_SECONDS:
            return data
        del _BARCODE_CACHE[barcode]
    return None


def _set_cached_product(barcode: str, data: dict) -> None:
    """Store successful product result in cache."""
    # Keep cache bounded to 500 entries
    if len(_BARCODE_CACHE) > 500:
        oldest_key = min(_BARCODE_CACHE, key=lambda k: _BARCODE_CACHE[k][0])
        del _BARCODE_CACHE[oldest_key]
    _BARCODE_CACHE[barcode] = (time.monotonic(), data)


async def fetch_from_upcitemdb(barcode: str, client: httpx.AsyncClient) -> dict | None:
    """Look up basic product details using UPCitemdb as secondary fallback."""
    url = "https://api.upcitemdb.com/prod/trial/lookup"

    try:
        response = await client.get(url, params={"upc": barcode})
    except (httpx.RequestError, httpx.TimeoutException) as exc:
        logger.warning("UPCitemdb request failed: %s", exc)
        return None

    if response.status_code == 404:
        return None

    try:
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        logger.warning("UPCitemdb error response: %s", exc)
        return None

    if payload.get("code") != "OK":
        return None

    items = payload.get("items") or []
    if not items:
        return None

    item = items[0]
    images = item.get("images") or []

    empty_nutrition = {
        "energy_kcal": None,
        "fat_g": None,
        "saturated_fat_g": None,
        "carbohydrates_g": None,
        "sugars_g": None,
        "fiber_g": None,
        "proteins_g": None,
        "salt_g": None,
        "sodium_mg": None,
    }

    nutrition_score = calculate_nutrition_score({
        "sugars_100g": None,
        "saturated-fat_100g": None,
        "salt_100g": None,
        "fiber_100g": None,
        "proteins_100g": None,
    })

    return {
        "success": True,
        "found": True,
        "data_source": "UPCitemdb",
        "data_source_url": "https://www.upcitemdb.com/",
        "barcode": item.get("ean") or item.get("upc") or barcode,
        "product": {
            "name": item.get("title"),
            "brands": item.get("brand"),
            "quantity": None,
            "countries": None,
            "ingredients_text": None,
            "ingredients_text_en": None,
            "allergens": None,
            "traces": None,
            "front_image_url": images[0] if images else None,
            "nutrition_per_100g": empty_nutrition,
            "nutrition_score": nutrition_score,
            "nutrition_grade": None,
            "nova_group": None,
            "additives_tags": [],
            "last_modified_timestamp": None,
        },
        "data_quality": {
            "ingredients_available": False,
            "nutrition_available": False,
            "warning": (
                "Basic product details came from UPCitemdb. "
                "Ingredient and nutrition information was not provided "
                "by this fallback source. Upload the physical package label "
                "to analyze its actual ingredients."
            ),
        },
    }


async def fetch_product_by_barcode(barcode: str) -> dict:
    """Look up a product by barcode in Open Food Facts, falling back to UPCitemdb."""
    barcode = barcode.strip()

    if not re.fullmatch(r"\d{8,14}", barcode):
        raise ValueError("Barcode must contain 8 to 14 numeric digits.")

    cached = _get_cached_product(barcode)
    if cached:
        return {**cached, "from_cache": True}

    async with httpx.AsyncClient(
        timeout=10.0,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        off_response = None
        off_network_error = None

        try:
            off_response = await client.get(
                f"{OPEN_FOOD_FACTS_URL}/{barcode}",
                params={"fields": REQUESTED_FIELDS},
            )
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            off_network_error = exc
            logger.warning("Open Food Facts request failed: %s", exc)

        # Case 1: Open Food Facts returned 404 (Not Found)
        if off_response is not None and off_response.status_code == 404:
            fallback = await fetch_from_upcitemdb(barcode, client)
            if fallback:
                _set_cached_product(barcode, fallback)
                return fallback

            return {
                "success": False,
                "found": False,
                "barcode": barcode,
                "message": (
                    "Product not found in either Open Food Facts or UPCitemdb. "
                    "Upload a photo of the ingredient label instead."
                ),
                "sources_checked": ["Open Food Facts", "UPCitemdb"],
            }

        # Case 2: Open Food Facts network error or 5xx server error
        if off_network_error is not None or (off_response is not None and off_response.status_code >= 500):
            fallback = await fetch_from_upcitemdb(barcode, client)
            if fallback:
                _set_cached_product(barcode, fallback)
                return fallback

            # If fallback also failed or didn't have it, propagate the actual connection issue
            if off_network_error:
                raise off_network_error
            off_response.raise_for_status()

        # Case 3: Open Food Facts returned 200 or client error (4xx other than 404)
        if off_response is not None:
            off_response.raise_for_status()
            payload = off_response.json()
        else:
            payload = {}

        if payload.get("status") != 1 or not payload.get("product"):
            fallback = await fetch_from_upcitemdb(barcode, client)
            if fallback:
                _set_cached_product(barcode, fallback)
                return fallback

            return {
                "success": False,
                "found": False,
                "barcode": barcode,
                "message": (
                    "Product not found in either database. "
                    "Upload a photo of the ingredient label instead."
                ),
                "sources_checked": ["Open Food Facts", "UPCitemdb"],
            }

        product = payload["product"]
        nutriments = product.get("nutriments") or {}

        def optional_text(key: str) -> str | None:
            value = product.get(key)
            return value if isinstance(value, str) and value.strip() else None

        def optional_number(key: str) -> float | None:
            value = nutriments.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
            return None

        product_url = optional_text("url") or (
            f"https://world.openfoodfacts.org/product/{barcode}"
        )

        nutrition_per_100g = {
            "energy_kcal": optional_number("energy-kcal_100g"),
            "fat_g": optional_number("fat_100g"),
            "saturated_fat_g": optional_number("saturated-fat_100g"),
            "carbohydrates_g": optional_number("carbohydrates_100g"),
            "sugars_g": optional_number("sugars_100g"),
            "fiber_g": optional_number("fiber_100g"),
            "proteins_g": optional_number("proteins_100g"),
            "salt_g": optional_number("salt_100g"),
            "sodium_mg": optional_number("sodium_100g"),
        }

        # Calculate experimental nutrition score from extracted nutrients
        score_input = {
            "sugars_100g": nutrition_per_100g["sugars_g"],
            "saturated-fat_100g": nutrition_per_100g["saturated_fat_g"],
            "salt_100g": nutrition_per_100g["salt_g"],
            "fiber_100g": nutrition_per_100g["fiber_g"],
            "proteins_100g": nutrition_per_100g["proteins_g"],
        }
        nutrition_score = calculate_nutrition_score(score_input)

        result = {
            "success": True,
            "found": True,
            "data_source": "Open Food Facts",
            "data_source_url": product_url,
            "barcode": product.get("code") or barcode,
            "product": {
                "name": optional_text("product_name"),
                "brands": optional_text("brands"),
                "quantity": optional_text("quantity"),
                "countries": optional_text("countries"),
                "ingredients_text": optional_text("ingredients_text"),
                "ingredients_text_en": optional_text("ingredients_text_en"),
                "allergens": optional_text("allergens"),
                "traces": optional_text("traces"),
                "front_image_url": optional_text("image_front_url"),
                "nutrition_per_100g": nutrition_per_100g,
                "nutrition_score": nutrition_score,
                "nutrition_grade": (
                    optional_text("nutrition_grades")
                    or optional_text("nutriscore_grade")
                ),
                "nova_group": product.get("nova_group"),
                "additives_tags": product.get("additives_tags") or [],
                "last_modified_timestamp": product.get("last_modified_t"),
            },
            "data_quality": {
                "ingredients_available": bool(
                    optional_text("ingredients_text")
                    or optional_text("ingredients_text_en")
                ),
                "nutrition_available": any(
                    value is not None for value in nutrition_per_100g.values()
                ),
                "warning": (
                    "Open Food Facts is a crowdsourced database. "
                    "Fields may be incomplete or outdated. "
                    "Verify essential ingredient and allergen details on the physical package."
                ),
            },
        }

        _set_cached_product(barcode, result)
        return result
