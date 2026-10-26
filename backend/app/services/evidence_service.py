
from copy import deepcopy


SOURCES = {
    "fssai": {
        "name": "Food Safety and Standards Authority of India",
        "url": "https://fssai.gov.in/",
        "source_type": "Indian regulatory reference",
    },
    "jecfa": {
        "name": "WHO/FAO JECFA database",
        "url": "https://apps.who.int/food-additives-contaminants-jecfa-database/",
        "source_type": "International scientific reference",
    },
}


ADDITIVE_EVIDENCE = {
    "330": {
        "code": "330",
        "name": "Citric acid",
        "purpose": "Acidity regulator",
    },
    "296": {
        "code": "296",
        "name": "Malic acid",
        "purpose": "Acidity regulator",
    },
    "334": {
        "code": "334",
        "name": "Tartaric acid",
        "purpose": "Acidity regulator",
    },
    "551": {
        "code": "551",
        "name": "Silicon dioxide",
        "purpose": "Anti-caking agent",
    },
    "160c": {
        "code": "160c",
        "name": "Paprika extract",
        "purpose": "Colouring agent",
    },
}


def _build_assessment(additive: dict) -> dict:
    return {
        **deepcopy(additive),
        "assessment_status": "insufficient_data",
        "identity_status": "catalogue_match_only",
        "short_term_effects": {
            "status": "not_assessed",
            "details": None,
        },
        "long_term_effects": {
            "status": "not_assessed",
            "details": None,
        },
        "exposure_assessment": {
            "status": "not_calculable",
            "amount_in_product": None,
            "serving_size_g": None,
            "consumption_frequency": None,
            "body_weight_kg": None,
            "estimated_intake": None,
            "reference_intake": None,
            "reason": (
                "The additive concentration and consumption details "
                "are not available. Do not infer exposure from ingredient "
                "order or presence alone."
            ),
        },
        "regulatory_status": "not_verified",
        "safety_conclusion": None,
        "evidence_quality": "not_individually_verified",
        "sources": deepcopy(SOURCES),
        "limitations": [
            "A catalogue match does not verify the substance on the package.",
            "Potential effects require substance-specific scientific evidence.",
            "Permitted uses can depend on food category and applicable rules.",
            "No product-specific safe-or-unsafe conclusion can be made "
            "without sufficient evidence and exposure information.",
        ],
        "disclaimer": (
            "This is an initial evidence record, not medical advice or "
            "a determination that a product is safe or unsafe."
        ),
    }


def list_additive_evidence() -> dict:
    """Return preliminary additive records and their assessment limitations."""
    records = [
        _build_assessment(ADDITIVE_EVIDENCE[code])
        for code in sorted(
            ADDITIVE_EVIDENCE,
            key=lambda value: (not value.isdigit(), value),
        )
    ]

    return {
        "count": len(records),
        "records": records,
        "disclaimer": (
            "Effects and exposure have not yet been individually assessed "
            "for these records. Do not interpret missing information as "
            "proof of safety or proof of harm."
        ),
    }


def get_additive_evidence(code: str) -> dict | None:
    """Return one preliminary additive assessment by its code."""
    normalized_code = code.strip().lower()
    additive = next(
        (
            item
            for key, item in ADDITIVE_EVIDENCE.items()
            if key.lower() == normalized_code
        ),
        None,
    )

    return _build_assessment(additive) if additive else None
