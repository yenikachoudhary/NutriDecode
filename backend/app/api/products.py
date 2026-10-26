
import httpx
from fastapi import APIRouter, HTTPException

from app.services.product_service import fetch_product_by_barcode

router = APIRouter(prefix="/products", tags=["Product Lookup"])


@router.get("/barcode/{barcode}")
async def lookup_product(barcode: str):
    """Find product ingredients and nutrition by barcode."""

    try:
        return await fetch_product_by_barcode(barcode)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="The product database took too long to respond.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="The external product database returned an error.",
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the external product database.",
        ) from exc

    except ValueError as exc:
        # Handles invalid JSON returned by the external service.
        raise HTTPException(
            status_code=502,
            detail="The external product database returned invalid data.",
        ) from exc
