
from fastapi import APIRouter, HTTPException

from app.services.evidence_service import (
    get_additive_evidence,
    list_additive_evidence,
)

router = APIRouter(prefix="/evidence", tags=["Evidence Database"])


@router.get("")
def list_evidence():
    """List additive references currently available in the local catalogue."""
    return list_additive_evidence()


@router.get("/{code}")
def additive_evidence(code: str):
    """Get identity information and reference links for one additive code."""
    record = get_additive_evidence(code)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No evidence catalogue entry found for code '{code}'.",
        )

    return record
