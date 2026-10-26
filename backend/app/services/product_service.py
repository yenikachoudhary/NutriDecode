
import re

import httpx
from app.services.nutrition_score_service import calculate_nutrition_score
from app.services.nutrition_score_service import calculate_nutrition_score

OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v2/product"

USER_AGENT = "NutriDecode/0.1 (food-label research prototype)"

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


async def fetch_from_upcitemdb(barcode: str, client: httpx.AsyncClient):
    """Look up basic product details using UPCitemdb."""
    url = "https://api.upcitemdb.com/prod/trial/lookup"

    try:
        response = await client.get(url, params={"upc": barcode})
    except httpx.RequestError:
        return None

    if response.status_code == 404:
        return None

    response.raise_for_status()
    payload = response.json()

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
                "by this fallback response. Upload the package label "
                "to analyze its ingredients."
            ),
        },
    }


async def fetch_product_by_barcode(barcode: str) -> dict:
    """Look up a product using its barcode in Open Food Facts."""

    barcode = barcode.strip()

    if not re.fullmatch(r"\d{8,14}", barcode):
        raise ValueError(
            "Barcode must contain 8 to 14 digits."
        )

    async with httpx.AsyncClient(
        timeout=12.0,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        
        try:
            response = await client.get(
                f"{OPEN_FOOD_FACTS_URL}/{barcode}",
                params={"fields": REQUESTED_FIELDS},
            )

            if response.status_code == 404:
                fallback = await fetch_from_upcitemdb(barcode, client)
                if fallback:
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

            response.raise_for_status()
            payload = response.json()

        except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
            fallback = await fetch_from_upcitemdb(barcode, client)
            if fallback:
                return fallback
            raise


    
    if payload.get("status") != 1 or not payload.get("product"):
        fallback = await fetch_from_upcitemdb(barcode, client)

        if fallback:
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

    def optional_text(key: str):
        value = product.get(key)
        return value if isinstance(value, str) and value.strip() else None

    def optional_number(key: str):
        value = nutriments.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value
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
    
    # Convert the existing API response fields to the scoring service's keys.
    score_input = {
        "sugars_100g": nutrition_per_100g["sugars_g"],
        "saturated-fat_100g": nutrition_per_100g["saturated_fat_g"],
        "salt_100g": nutrition_per_100g["salt_g"],
        "fiber_100g": nutrition_per_100g["fiber_g"],
        "proteins_100g": nutrition_per_100g["proteins_g"],
    }

    nutrition_score = calculate_nutrition_score(score_input)


    return {
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
                value is not None
                for value in nutrition_per_100g.values()
            ),
            "warning": (
                "Open Food Facts is a collaborative database. "
                "Fields may be missing, outdated or incorrect. "
                "Verify important details against the physical package."
            ),
        },
    }
