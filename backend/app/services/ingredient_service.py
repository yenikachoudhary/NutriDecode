
import re


ADDITIVE_DATABASE = {
    "330": {
        "name": "Citric acid",
        "purpose": "Acidity regulator",
    },
    "296": {
        "name": "Malic acid",
        "purpose": "Acidity regulator",
    },
    "334": {
        "name": "Tartaric acid",
        "purpose": "Acidity regulator",
    },
    "551": {
        "name": "Silicon dioxide",
        "purpose": "Anti-caking agent",
    },
    "160c": {
        "name": "Paprika extract",
        "purpose": "Colouring agent",
    },
}

KNOWN_INGREDIENTS = {
    "potato",
    "edible vegetable",
    "edible vegetable oil",
    "palmolein",
    "palm olein",
    "palm oil",
    "rice bran oil",
    "seasoning",
    "spices",
    "condiments",
    "spices & condiments",
    "iodised salt",
    "iodized salt",
    "salt",
    "maltodextrin",
    "black salt",
    "sugar",
    "tomato powder",
    "onion",
    "garlic",
    "natural flavouring substances",
    "natural flavoring substances",
    "flavouring substances",
    "flavoring substances",
    "citric acid",
    "malic acid",
    "tartaric acid",
    "silicon dioxide",
    "paprika extract",
}

ALIASES = {
    "palmolein": "palm olein",
    "iodised salt": "iodized salt",
    "colour": "color",
    "anticaking agent": "anti-caking agent",
}


def normalize_ingredient(value: str) -> str:
    """Normalize whitespace, punctuation and known label aliases."""

    value = value.lower().strip()
    value = re.sub(r"^[\s~'\".]+|[\s~'\".]+$", "", value)
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" ,;:.")
    return ALIASES.get(value, value)


def analyze_ingredients(text: str) -> dict:
    """Identify known ingredients and additive codes in label text."""

    if not text or not text.strip():
        raise ValueError("Ingredient text cannot be empty.")

    cleaned = text.lower()
    cleaned = cleaned.replace("\\dentical", "identical")
    cleaned = cleaned.replace("\u2018", "'").replace("\u2019", "'")
    cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"')

    # Extract codes before removing additive descriptions.
    code_pattern = re.compile(
        r"(?<![a-z0-9])(?:160c|330|296|334|551)(?![a-z0-9])",
        re.IGNORECASE,
    )
    codes_found = {
        match.group(0).lower()
        for match in code_pattern.finditer(cleaned)
    }

    # Remove the ingredients heading.
    cleaned = re.sub(
        r"\bingredients?\s*:",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove additive groups whose codes have already been captured.
    cleaned = re.sub(
        r"\bacidity\s+regulators?\s*\([^)]*\)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\banti[\s-]*caking\s+agent\s*\([^)]*\)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\bcolou?r\s*\([^)]*\)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove the descriptive flavouring phrase, not the whole ingredient list.
    cleaned = re.sub(
        r"\bflavou?r\s*\(\s*natural\s+and\s+nature\s+"
        r"identical\s+flavou?ring\s+substances\s*\)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # These are label notes rather than ingredient names.
    cleaned = re.sub(
        r"\bas\s+flavou?ring\s+agent\b.*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Preserve onion and garlic when the label says "Contains Onion and Garlic".
    cleaned = re.sub(r"\bcontains\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\band\b", ",", cleaned, flags=re.IGNORECASE)

    # Repair common OCR formatting issues around grouped ingredients.
    cleaned = re.sub(r"\)\s*\(", ",", cleaned)
    cleaned = cleaned.replace("(", ",").replace(")", ",")
    cleaned = cleaned.replace("\n", ",")
    cleaned = re.sub(r"[,;]+", ",", cleaned)

    ingredients = []
    seen = set()

    for part in cleaned.split(","):
        raw = part.strip(" \t\r\n~'\".")
        if not raw:
            continue

        normalized = normalize_ingredient(raw)

        if not normalized or normalized in seen:
            continue

        # Ignore stray label fragments and OCR punctuation.
        if normalized in {"ingredients", "agent"}:
            continue

        seen.add(normalized)
        recognized = normalized in KNOWN_INGREDIENTS

        ingredients.append({
            "raw_text": raw,
            "normalized_name": normalized,
            "recognized": recognized,
            "review_required": not recognized,
        })

    additives = []
    for code in sorted(
        codes_found,
        key=lambda item: (
            not item.isdigit(),
            int(item) if item.isdigit() else item,
        ),
    ):
        reference = ADDITIVE_DATABASE.get(code)
        if reference:
            additives.append({
                "code": code,
                "name": reference["name"],
                "purpose": reference["purpose"],
                "evidence_status": "identity_reference",
                "safety_conclusion": None,
            })

    review_required = any(
        ingredient["review_required"] for ingredient in ingredients
    )

    return {
        "ingredients": ingredients,
        "additives": additives,
        "additive_codes_found": sorted(codes_found),
        "review_required": review_required,
        "disclaimer": (
            "This prototype identifies label terms; it does not determine "
            "toxicity or personal health risk."
        ),
    }
