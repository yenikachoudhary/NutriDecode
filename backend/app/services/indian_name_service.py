
import re


# Starter dictionary. These are curated aliases, not an exhaustive
# dictionary of Indian regional ingredient names.
ALIASES = {
    "salt": ("salt", "English"),
    "namak": ("salt", "Hindi/Urdu"),
    "uppu": ("salt", "Tamil/Telugu/Kannada/Malayalam"),
    "sugar": ("sugar", "English"),
    "chini": ("sugar", "Hindi"),
    "cheeni": ("sugar", "Hindi"),
    "sakkarai": ("sugar", "Tamil"),
    "sakkare": ("sugar", "Kannada"),
    "chakkera": ("sugar", "Telugu"),
    "chakkara": ("sugar", "Malayalam"),
    "turmeric": ("turmeric", "English"),
    "haldi": ("turmeric", "Hindi/Urdu"),
    "manjal": ("turmeric", "Tamil/Malayalam"),
    "pasupu": ("turmeric", "Telugu"),
    "arishina": ("turmeric", "Kannada"),
    "holud": ("turmeric", "Bengali"),
    "halad": ("turmeric", "Marathi"),
    "chilli": ("chilli pepper", "English"),
    "chili": ("chilli pepper", "English"),
    "mirch": ("chilli pepper", "Hindi/Urdu"),
    "mirchi": ("chilli pepper", "Hindi/Marathi"),
    "milagai": ("chilli pepper", "Tamil"),
    "mirapakayalu": ("chilli pepper", "Telugu"),
    "menasinakayi": ("chilli pepper", "Kannada"),
    "mulaku": ("chilli pepper", "Malayalam"),
    "lonka": ("chilli pepper", "Bengali"),
    "cumin": ("cumin", "English"),
    "jeera": ("cumin", "Hindi/Urdu"),
    "seeragam": ("cumin", "Tamil"),
    "jeelakarra": ("cumin", "Telugu"),
    "jeerige": ("cumin", "Kannada"),
    "coriander": ("coriander", "English"),
    "dhania": ("coriander", "Hindi"),
    "kothamalli": ("coriander", "Tamil"),
    "kothimeera": ("coriander", "Telugu"),
    "kottambari": ("coriander", "Kannada"),
    "coconut oil": ("coconut oil", "English"),
    "nariyal tel": ("coconut oil", "Hindi"),
    "narial tel": ("coconut oil", "Hindi"),
    "ginger": ("ginger", "English"),
    "adrak": ("ginger", "Hindi/Urdu"),
    "inji": ("ginger", "Tamil/Malayalam"),
    "allam": ("ginger", "Telugu"),
    "shunti": ("ginger", "Kannada"),
    "garlic": ("garlic", "English"),
    "lehsun": ("garlic", "Hindi"),
    "poondu": ("garlic", "Tamil"),
    "vellulli": ("garlic", "Telugu"),
    "bellulli": ("garlic", "Kannada"),
    "potato": ("potato", "English"),
    "aloo": ("potato", "Hindi/Urdu"),
    "urulai kizhangu": ("potato", "Tamil"),
    "bangaladumpa": ("potato", "Telugu"),
    "alugadde": ("potato", "Kannada"),
    "onion": ("onion", "English"),
    "pyaaz": ("onion", "Hindi/Urdu"),
    "vengayam": ("onion", "Tamil"),
    "ullipaya": ("onion", "Telugu"),
    "eerulli": ("onion", "Kannada"),
    "atta": ("whole wheat flour", "Hindi"),
    "whole wheat flour": ("whole wheat flour", "English"),
    "maida": ("refined wheat flour", "Hindi"),
    "refined wheat flour": ("refined wheat flour", "English"),
}


def normalize_name(name: str) -> str:
    """Normalize text for exact alias lookup."""

    value = name.casefold().strip()
    value = re.sub(r"[\s\-]+", " ", value)
    value = re.sub(r"^[^\w]+|[^\w]+$", "", value)
    return value


def resolve_indian_name(name: str) -> dict:
    """Resolve a known regional alias without guessing unknown terms."""

    normalized = normalize_name(name)

    if not normalized:
        return {
            "input_name": name,
            "normalized_input": normalized,
            "canonical_name": None,
            "matched": False,
            "language": None,
            "confidence": 0.0,
            "status": "needs_review",
        }

    match = ALIASES.get(normalized)

    if match:
        canonical_name, language = match
        return {
            "input_name": name,
            "normalized_input": normalized,
            "canonical_name": canonical_name,
            "matched": True,
            "language": language,
            "confidence": 1.0,
            "status": "exact_dictionary_match",
        }

    return {
        "input_name": name,
        "normalized_input": normalized,
        "canonical_name": None,
        "matched": False,
        "language": None,
        "confidence": 0.0,
        "status": "needs_review",
    }
