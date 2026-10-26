
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
    
    # Additional common Indian ingredient names
    "methi": ("fenugreek", "Hindi"),
    "vendhayam": ("fenugreek", "Tamil"),
    "menthulu": ("fenugreek", "Telugu"),
    "menthya": ("fenugreek", "Kannada"),

    "saunf": ("fennel", "Hindi/Urdu"),
    "perunjeeragam": ("fennel", "Tamil"),
    "sompu": ("fennel", "Telugu"),
    "badishep": ("fennel", "Marathi"),

    "rai": ("mustard", "Hindi"),
    "sarson": ("mustard", "Hindi/Punjabi"),
    "kadugu": ("mustard", "Tamil"),
    "avalu": ("mustard", "Telugu"),
    "sasive": ("mustard", "Kannada"),

    "kali mirch": ("black pepper", "Hindi"),
    "milagu": ("black pepper", "Tamil"),
    "miriyalu": ("black pepper", "Telugu"),
    "kare menasu": ("black pepper", "Kannada"),

    "elaichi": ("cardamom", "Hindi"),
    "elakkai": ("cardamom", "Tamil"),
    "yelakulu": ("cardamom", "Telugu"),
    "elakki": ("cardamom", "Kannada"),

    "dalchini": ("cinnamon", "Hindi"),
    "pattai": ("cinnamon", "Tamil"),
    "dalchina chekka": ("cinnamon", "Telugu"),
    "lavangam": ("clove", "Tamil"),
    "laung": ("clove", "Hindi"),
    "lavangalu": ("clove", "Telugu"),

    "hing": ("asafoetida", "Hindi"),
    "perungayam": ("asafoetida", "Tamil"),
    "inguva": ("asafoetida", "Telugu"),

    "besan": ("chickpea flour", "Hindi"),
    "kadalai maavu": ("chickpea flour", "Tamil"),
    "senagapindi": ("chickpea flour", "Telugu"),

    "chawal": ("rice", "Hindi"),
    "arisi": ("rice", "Tamil"),
    "biyyam": ("rice", "Telugu"),
    "akki": ("rice", "Kannada"),

    "doodh": ("milk", "Hindi/Urdu"),
    "paal": ("milk", "Tamil/Malayalam"),
    "paalu": ("milk", "Telugu"),
    "haalu": ("milk", "Kannada"),

    "dahi": ("curd", "Hindi"),
    "thayir": ("curd", "Tamil"),
    "perugu": ("curd", "Telugu"),
    "mosaru": ("curd", "Kannada"),
    "doi": ("curd", "Bengali"),

    "ghee": ("ghee", "English/Hindi"),
    "nei": ("ghee", "Tamil"),
    "neyyi": ("ghee", "Telugu"),

    "nimbu": ("lemon", "Hindi"),
    "elumichai": ("lemon", "Tamil"),
    "nimma": ("lemon", "Kannada"),
    "nimmakaya": ("lemon", "Telugu"),

    "tamatar": ("tomato", "Hindi/Urdu"),
    "thakkali": ("tomato", "Tamil"),
    "pandutamota": ("tomato", "Telugu"),

}


def normalize_name(name: str) -> str:
    """Normalize text for exact alias lookup."""

    value = name.casefold().strip()
    value = re.sub(r"[\s\-]+", " ", value)
    value = re.sub(r"^[^\w]+|[^\w]+$", "", value)
    return value


def find_alias_match(normalized: str):
    """Find an exact alias, or remove known descriptive words cautiously."""

    # Exact matches always take priority.
    if normalized in ALIASES:
        return ALIASES[normalized], normalized, True

    prefixes = {"organic", "pure", "natural", "fresh", "dried", "whole"}
    suffixes = {
        "powder", "powdered", "ground", "crushed",
        "dried", "fresh", "whole", "seeds", "seed",
        "leaves", "leaf", "paste", "roasted",
    }

    words = normalized.split()
    if not words:
        return None, normalized, False

    # Remove only recognized descriptors at the beginning or end.
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
        return ALIASES[candidate], candidate, candidate != normalized

    return None, normalized, False


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


    match, matched_alias, was_normalized = find_alias_match(normalized)

    if match:
        canonical_name, language = match
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
