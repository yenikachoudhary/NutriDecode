import logging
import httpx
from fastapi import APIRouter, HTTPException, Query

from app.services.product_service import fetch_product_by_barcode
from app.services.product_discovery_service import search_candidate_products

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["Product Lookup"])


@router.get("/barcode/{barcode}")
async def lookup_product(barcode: str):
    """Find product ingredients and nutrition by barcode."""
    try:
        return await fetch_product_by_barcode(barcode)

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except httpx.TimeoutException as exc:
        logger.warning("Product lookup timed out: %s", exc)
        raise HTTPException(
            status_code=504,
            detail="The product database took too long to respond.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        logger.error(
            "External product database returned HTTP %s: %s",
            exc.response.status_code,
            exc.response.text[:500],
        )
        raise HTTPException(
            status_code=502,
            detail="The external product database returned an error.",
        ) from exc

    except httpx.RequestError as exc:
        logger.error("Product database connection failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the external product database.",
        ) from exc


@router.get("/search")
async def search_products(
    query: str = Query(..., min_length=1, description="Product brand or keyword to discover candidate records."),
    limit: int = Query(5, ge=1, le=15, description="Maximum candidate records to retrieve."),
):
    """Search for candidate product records in Open Food Facts when barcode is unknown or missing."""
    try:
        return await search_candidate_products(query=query, limit=limit)
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="The candidate search provider timed out.",
        ) from exc
    except Exception as exc:
        logger.error("Candidate search failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Error searching product candidates from the registry.",
        ) from exc
