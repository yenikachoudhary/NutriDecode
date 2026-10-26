
import re

ADDITIVE_DATABASE = {
    "330": {"name": "Citric acid", "purpose": "Acidity regulator"},
    "296": {"name": "Malic acid", "purpose": "Acidity regulator"},
    "334": {"name": "Tartaric acid", "purpose": "Acidity regulator"},
    "551": {"name": "Silicon dioxide", "purpose": "Anti-caking agent"},
    "160c": {"name": "Paprika extract", "purpose": "Colouring agent"},
}

ALIASES = {
    "iodised salt": "iodized salt",
    "palmolein": "palm olein",
}

KNOWN_INGREDIENTS = {
    "potato", "edible vegetable oil", "palm olein", "palm oil",
    "rice bran oil", "seasoning", "spices", "condiments",
    "iodized salt", "salt", "maltodextrin", "black salt", "sugar",
    "tomato powder", "citric acid", "malic acid", "tartaric acid",
    "natural flavouring substances", "nature identical flavouring substances",
    "silicon dioxide", "paprika extract", "onion", "garlic",
}


def analyze_ingredients(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Provide non-empty label text.")

    cleaned = re.sub(r"\s+", " ", text).strip()

    match = re.search(r"\bingredients?\s*:", cleaned, re.IGNORECASE)
    if match:
        cleaned = cleaned[match.end():]

    cleaned = re.split(
        r"\bas flavouring agent\b|\bcontains onion and garlic\b",
        cleaned,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    codes_found = re.findall(
        r"(?<![A-Za-z0-9])(?:INS\s*)?(330|296|334|551|160c)(?![A-Za-z0-9])",
        cleaned,
        flags=re.IGNORECASE,
    )

    additives = []
    seen_codes = set()

    for code in codes_found:
        normalized_code = code.lower()
        if normalized_code not in seen_codes:
            seen_codes.add(normalized_code)
            info = ADDITIVE_DATABASE[normalized_code]
            additives.append({
                "code": normalized_code,
                "name": info["name"],
                "purpose": info["purpose"],
                "evidence_status": "identity_reference",
                "safety_conclusion": None,
            })

    ingredient_text = re.sub(
        r"\([^)]*(?:330|296|334|551|160c)[^)]*\)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )

    ingredients = []
    seen_names = set()

    for candidate in re.split(r"[,;]", ingredient_text):
        item = candidate.strip(" \t\r\n.()'\"“”‘’")
        item = re.sub(r"^[~*]+", "", item).strip()

        if not item:
            continue

        normalized = re.sub(r"\s+", " ", item).lower()
        normalized = ALIASES.get(normalized, normalized)

        if normalized in seen_names:
            continue
        seen_names.add(normalized)

        known = normalized in KNOWN_INGREDIENTS
        ingredients.append({
            "raw_text": item,
            "normalized_name": normalized,
            "recognized": known,
            "review_required": not known,
        })

    return {
        "ingredients": ingredients,
        "additives": additives,
        "additive_codes_found": sorted(seen_codes),
        "review_required": any(
            item["review_required"] for item in ingredients
        ),
        "disclaimer": (
            "This prototype identifies label terms; it does not "
            "determine toxicity or personal health risk."
        ),
    }
