"""Ingredient and additive parsing service.

Parses unstructured food-label text, extracts additive codes (INS/E-numbers),
normalizes chemical and common ingredient names, and detects unrecognized terms
requiring manual review.
"""

import re
from app.services.evidence_service import ADDITIVE_EVIDENCE

# Additive reference dictionary populated from evidence records
ADDITIVE_DATABASE = {
    code: {
        "name": record["name"],
        "purpose": record["purpose"],
    }
    for code, record in ADDITIVE_EVIDENCE.items()
}

KNOWN_INGREDIENTS = {
    "potato",
    "edible vegetable",
    "edible vegetable oil",
    "vegetable oil",
    "palmolein",
    "palm olein",
    "palm oil",
    "refined palm oil",
    "rice bran oil",
    "refined rice bran oil",
    "soybean oil",
    "sunflower oil",
    "mustard oil",
    "groundnut oil",
    "peanut oil",
    "sesame oil",
    "seasoning",
    "spices",
    "condiments",
    "spices & condiments",
    "spices and condiments",
    "mixed spices",
    "iodised salt",
    "iodized salt",
    "salt",
    "black salt",
    "rock salt",
    "sugar",
    "refined sugar",
    "cane sugar",
    "brown sugar",
    "jaggery",
    "maltodextrin",
    "dextrose",
    "glucose",
    "liquid glucose",
    "invert sugar syrup",
    "starch",
    "edible starch",
    "corn starch",
    "maize starch",
    "potato starch",
    "tapioca starch",
    "wheat flour",
    "refined wheat flour",
    "refined wheat flour maida",
    "maida",
    "whole wheat flour",
    "atta",
    "whole wheat flour atta",
    "wheat gluten",
    "semolina",
    "suji",
    "rava",
    "gram flour",
    "besan",
    "chickpea flour",
    "rice flour",
    "corn flour",
    "oat flour",
    "rolled oats",
    "milk solids",
    "skimmed milk powder",
    "whole milk powder",
    "dairy whitener",
    "whey powder",
    "whey protein concentrate",
    "butter",
    "ghee",
    "clarified butter",
    "cheese powder",
    "cocoa solids",
    "cocoa butter",
    "cocoa mass",
    "water",
    "purified water",
    "mineral water",
    "tomato powder",
    "tomato paste",
    "dehydrated onion",
    "onion",
    "onion powder",
    "garlic",
    "garlic powder",
    "dehydrated garlic",
    "ginger",
    "ginger powder",
    "chilli powder",
    "red chilli",
    "green chilli",
    "black pepper",
    "cumin",
    "cumin powder",
    "turmeric",
    "turmeric powder",
    "coriander",
    "coriander powder",
    "cardamom",
    "cinnamon",
    "clove",
    "fenugreek",
    "asafoetida",
    "fennel",
    "alphonso mango pulp",
    "mango pulp",
    "fruit pulp",
    "fruit juice concentrate",
    "yeast",
    "yeast extract",
    "hydrolysed peanut protein",
    "hydrolysed vegetable protein",
    "soy protein isolate",
    "natural flavouring substances",
    "natural flavoring substances",
    "nature identical flavouring substances",
    "nature identical flavoring substances",
    "flavouring substances",
    "flavoring substances",
    "citric acid",
    "malic acid",
    "tartaric acid",
    "silicon dioxide",
    "paprika extract",
    "soy lecithin",
    "lecithin",
    "pectin",
    "ascorbic acid",
    "sodium bicarbonate",
    "ammonium bicarbonate",
    "potassium chloride",
    "beta carotenes",
    "sodium benzoate",
    "potassium sorbate",
    "mixed tocopherols",
}

ALIASES = {
    "palmolein": "palm olein",
    "iodised salt": "iodized salt",
    "colour": "color",
    "anticaking agent": "anti-caking agent",
    "refined wheat flour (maida)": "refined wheat flour",
    "whole wheat flour (atta)": "whole wheat flour",
    "sugar (sucrose)": "sugar",
}


def normalize_ingredient(value: str) -> str:
    """Normalize whitespace, punctuation and known label aliases."""
    value = value.lower().strip()
    # Strip leading/trailing punctuation and quotes
    value = re.sub(r"^[\s~'\".:\-]+|[\s~'\".:\-]+$", "", value)
    # Strip percentage if appended like "wheat flour 62%"
    value = re.sub(r"\s*\d+(\.\d+)?\s*%\s*", "", value)
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" ,;:.")
    return ALIASES.get(value, value)


def _clean_code(code_str: str) -> str:
    """Clean and normalize an additive code string."""
    cleaned = code_str.lower().strip()
    cleaned = re.sub(r"^(?:ins|e)[\s\-\.]*", "", cleaned)
    # Normalize roman numerals in parentheses e.g. 500(ii) -> 500 or keep 500(ii)
    # If base code is in ADDITIVE_DATABASE, use that
    base = re.sub(r"[\(\)\s]", "", cleaned)
    if base in ADDITIVE_DATABASE:
        return base
    digits_only = "".join(filter(str.isdigit, cleaned))
    if digits_only in ADDITIVE_DATABASE:
        return digits_only
    # Remove parentheses: 500(ii) -> 500ii
    cleaned = re.sub(r"[\(\)]", "", cleaned).strip()
    return cleaned


def analyze_ingredients(text: str) -> dict:
    """Identify known ingredients and additive codes in label text."""
    if not text or not text.strip():
        raise ValueError("Ingredient text cannot be empty.")

    cleaned = text.lower()
    cleaned = cleaned.replace("\\dentical", "identical")
    cleaned = cleaned.replace("\u2018", "'").replace("\u2019", "'")
    cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"')

    # Extract all additive codes (INS numbers, E-numbers, and bare catalogue codes)
    codes_found = set()

    # Pattern 1: Explicit INS or E prefix, e.g., "INS 330", "INS 500(ii)", "E150d", "INS-322"
    explicit_pattern = re.compile(
        r"\b(?:ins|e)[\s\-\.]*(\d{3,4}[a-z]?(?:\s*\([i|v|x]+\))?)\b",
        re.IGNORECASE,
    )
    for match in explicit_pattern.finditer(cleaned):
        code_raw = match.group(1)
        normalized_c = _clean_code(code_raw)
        if normalized_c:
            codes_found.add(normalized_c)

    # Pattern 2: Numbers inside additive category clauses, e.g. "Acidity Regulators (330, 296, 334)"
    category_clause_pattern = re.compile(
        r"\b(?:acidity\s+regulators?|anti[\s-]*caking\s+agents?|colou?rs?|flavo?u?r\s+enhancers?|raising\s+agents?|emulsifiers?|antioxidants?|preservatives?|stabilizers?|thickeners?|gelling\s+agents?)\s*\(([^)]+)\)",
        re.IGNORECASE,
    )
    for clause_match in category_clause_pattern.finditer(cleaned):
        inside = clause_match.group(1)
        # Find any additive numbers inside the parentheses
        for num in re.findall(r"\b(\d{3,4}[a-z]?(?:\s*\([i|v|x]+\))?)\b", inside, re.IGNORECASE):
            norm = _clean_code(num)
            if norm:
                codes_found.add(norm)

    # Pattern 3: Explicit check for known catalogue codes if present as isolated tokens
    catalogue_keys = "|".join(re.escape(k) for k in ADDITIVE_DATABASE.keys())
    standalone_code_pattern = re.compile(
        rf"(?<![a-z0-9])({catalogue_keys})(?![a-z0-9])",
        re.IGNORECASE,
    )
    for match in standalone_code_pattern.finditer(cleaned):
        matched_code = match.group(1).lower()
        codes_found.add(matched_code)

    # Remove the ingredients heading and section headers
    cleaned = re.sub(r"\bingredients?\s*:", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(?:noodle\s+cake|tastemaker|seasoning\s+mix)\s*:", "", cleaned, flags=re.IGNORECASE)

    # Remove additive groups whose codes have already been captured
    cleaned = re.sub(
        r"\b(?:acidity\s+regulators?|anti[\s-]*caking\s+agents?|colou?rs?|flavo?u?r\s+enhancers?|raising\s+agents?|emulsifiers?|antioxidants?|preservatives?|stabilizers?|thickeners?|gelling\s+agents?)\s*\([^)]*\)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove descriptive flavouring phrase, not the whole ingredient list
    cleaned = re.sub(
        r"\bflavou?r\s*\(\s*natural\s+and\s+nature\s+identical\s+flavou?ring\s+substances\s*\)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\bnature\s+identical\s+flavou?ring\s+substances\b(?:\s*\([^)]*\))?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\bas\s+flavou?ring\s+agent\b.*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove "contains ... allergens" statements at end
    cleaned = re.sub(r"\bcontains\s+(?:wheat|soy|milk|gluten|peanut|nuts|egg|sulphite)[^.]*\.?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bmay\s+contain\s+[^.]*\.?", "", cleaned, flags=re.IGNORECASE)

    # Preserve onion and garlic when the label says "Contains Onion and Garlic"
    cleaned = re.sub(r"\bcontains\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\band\b", ",", cleaned, flags=re.IGNORECASE)

    # Repair common OCR formatting issues around grouped ingredients
    cleaned = re.sub(r"\)\s*\(", ",", cleaned)
    cleaned = cleaned.replace("(", ",").replace(")", ",")
    cleaned = cleaned.replace("\n", ",")
    cleaned = re.sub(r"[,;]+", ",", cleaned)

    ingredients = []
    seen = set()

    for part in cleaned.split(","):
        raw = part.strip(" \t\r\n~'\".:")
        if not raw:
            continue

        normalized = normalize_ingredient(raw)

        if not normalized or normalized in seen:
            continue

        # Ignore stray label fragments and OCR punctuation
        if normalized in {"ingredients", "agent", "agents", "contains", "food", "substances"}:
            continue
        # Ignore purely numeric fragments
        if re.fullmatch(r"[\d\.\s%]+", normalized):
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
    # Sort codes with numeric first, then alphanumeric
    sorted_codes = sorted(
        codes_found,
        key=lambda item: (
            not item.isdigit(),
            int(item) if item.isdigit() else item,
        ),
    )

    for code in sorted_codes:
        reference = ADDITIVE_DATABASE.get(code)
        if not reference:
            # Fallback check stripping non-digits
            digits = "".join(filter(str.isdigit, code))
            if digits in ADDITIVE_DATABASE:
                reference = ADDITIVE_DATABASE[digits]

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
        "additive_codes_found": sorted_codes,
        "review_required": review_required,
        "disclaimer": (
            "This prototype identifies label terms; it does not determine "
            "toxicity or personal health risk."
        ),
    }
