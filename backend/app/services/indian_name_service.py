
import json
import re
from pathlib import Path


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "indian_ingredient_aliases.json"
)


def normalize_name(name: str) -> str:
    """Normalize text for consistent ingredient alias lookup."""
    value = name.casefold().strip()
    value = re.sub(r"[\s\-]+", " ", value)
    value = re.sub(r"^[^\w]+|[^\w]+$", "", value)
    return value


def _load_alias_data():
    """Load aliases and their provenance metadata from JSON."""
    if not DATA_PATH.is_file():
        raise FileNotFoundError(
            f"Ingredient alias dataset not found: {DATA_PATH}"
        )

    records = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    if not isinstance(records, list):
        raise ValueError("Ingredient alias dataset must contain a JSON list.")

    aliases = {}
    metadata = {}

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each alias record must be a JSON object.")

        alias = normalize_name(str(record.get("alias", "")))
        canonical_name = str(record.get("canonical_name", "")).strip()
        language = str(record.get("language", "")).strip()

        if not alias or not canonical_name or not language:
            continue

        if alias in aliases:
            existing_name = aliases[alias][0]
            if existing_name != canonical_name:
                raise ValueError(
                    f"Conflicting canonical names for alias: {alias}"
                )
            continue

        aliases[alias] = (canonical_name, language)
        metadata[alias] = {
            "source": record.get("source", "unspecified"),
            "review_status": record.get(
                "review_status", "needs_source_review"
            ),
        }

    return aliases, metadata


ALIASES, ALIAS_METADATA = _load_alias_data()


def find_alias_match(normalized: str):
    """Find an exact alias or cautiously remove known descriptors."""

    # Exact matches take priority.
    if normalized in ALIASES:
        return ALIASES[normalized], normalized, False

    prefixes = {"organic", "pure", "natural", "fresh", "dried", "whole"}
    suffixes = {
        "powder",
        "powdered",
        "ground",
        "crushed",
        "dried",
        "fresh",
        "whole",
        "seeds",
        "seed",
        "leaves",
        "leaf",
        "paste",
        "roasted",
    }

    words = normalized.split()
    if not words:
        return None, normalized, False

    original = normalized
    changed = True

    while changed and words:
        changed = False

        if words and words[0] in prefixes:
            words.pop(0)
            changed = True

        if words and words[-1] in suffixes:
            words.pop()
            changed = True

    candidate = " ".join(words)

    if candidate and candidate in ALIASES:
        return ALIASES[candidate], candidate, candidate != original

    return None, normalized, False


def resolve_indian_name(name: str) -> dict:
    """Resolve a known alias without guessing unknown ingredient names."""

    normalized = normalize_name(name or "")

    if not normalized:
        return {
            "input_name": name,
            "normalized_input": normalized,
            "canonical_name": None,
            "matched": False,
            "language": None,
            "confidence": 0.0,
            "status": "needs_review",
            "source": None,
            "review_status": None,
        }

    match, matched_alias, was_normalized = find_alias_match(normalized)

    if match:
        canonical_name, language = match
        alias_metadata = ALIAS_METADATA.get(matched_alias, {})

        return {
            "input_name": name,
            "normalized_input": normalized,
            "canonical_name": canonical_name,
            "matched": True,
            "language": language,
            "confidence": 1.0,
            "matched_alias": matched_alias,
            "status": (
                "normalized_alias_match"
                if was_normalized
                else "exact_dictionary_match"
            ),
            "source": alias_metadata.get("source", "unspecified"),
            "review_status": alias_metadata.get(
                "review_status", "needs_source_review"
            ),
        }

    return {
        "input_name": name,
        "normalized_input": normalized,
        "canonical_name": None,
        "matched": False,
        "language": None,
        "confidence": 0.0,
        "status": "needs_review",
        "source": None,
        "review_status": None,
    }
