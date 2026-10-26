
from copy import deepcopy


SOURCES = {
    "fssai": {
        "name": "Food Safety and Standards Authority of India",
        "url": (
            "https://fssai.gov.in/food-law/regulations/"
            "compendium/food-products-standards"
        ),
        "source_type": "Indian regulatory reference",
        "scope": (
            "Food product standards and food additives regulations. "
            "Check the latest applicable notifications and amendments."
        ),
    },
    "jecfa": {
        "name": "WHO/FAO JECFA database",
        "url": (
            "https://apps.who.int/"
            "food-additives-contaminants-jecfa-database/"
        ),
        "source_type": "International scientific reference",
        "scope": (
            "Searchable evaluations and technical references for food "
            "additives and other substances. Individual records must be "
            "checked before making substance-specific claims."
        ),
    },
}


ADDITIVE_EVIDENCE = {
    "330": {
        "code": "330",
        "name": "Citric acid",
        "purpose": "Acidity regulator",
        "description": (
            "Identified in this prototype as citric acid, an additive "
            "associated with acidity regulation."
        ),
    },
    "296": {
        "code": "296",
        "name": "Malic acid",
        "purpose": "Acidity regulator",
        "description": (
            "Identified in this prototype as malic acid, an additive "
            "associated with acidity regulation."
        ),
    },
    "334": {
        "code": "334",
        "name": "Tartaric acid",
        "purpose": "Acidity regulator",
        "description": (
            "Identified in this prototype as tartaric acid, an additive "
            "associated with acidity regulation."
        ),
    },
    "551": {
        "code": "551",
        "name": "Silicon dioxide",
        "purpose": "Anti-caking agent",
        "description": (
            "Identified in this prototype as silicon dioxide, used as an "
            "anti-caking agent in some food applications."
        ),
    },
    "160c": {
        "code": "160c",
        "name": "Paprika extract",
        "purpose": "Colouring agent",
        "description": (
            "Identified in this prototype as paprika extract, a colour "
            "additive."
        ),
    },
}


def list_additive_evidence() -> dict:
    """Return the local additive catalogue with source links."""

    records = []

    for code in sorted(
        ADDITIVE_EVIDENCE,
        key=lambda value: (not value.isdigit(), value),
    ):
        record = deepcopy(ADDITIVE_EVIDENCE[code])
        record.update({
            "evidence_status": "identity_reference_only",
            "safety_conclusion": None,
            "sources": deepcopy(SOURCES),
            "interpretation_note": (
                "These links are reference starting points, not proof that "
                "this specific additive has been individually verified "
                "against every claim shown here."
            ),
            "regulatory_note": (
                "Permitted uses and limits can depend on food category "
                "and applicable regulations. This endpoint does not "
                "determine regulatory compliance."
            ),
        })
        records.append(record)

    return {
        "count": len(records),
        "records": records,
        "disclaimer": (
            "This catalogue provides preliminary identity information, "
            "not a toxicity assessment, medical recommendation, or "
            "determination that a food is safe or unsafe."
        ),
    }


def get_additive_evidence(code: str) -> dict | None:
    """Find one additive by its INS-style code."""

    normalized_code = code.strip().lower()
    catalogue = list_additive_evidence()

    for record in catalogue["records"]:
        if record["code"].lower() == normalized_code:
            return record

    return None
