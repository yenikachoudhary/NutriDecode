
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.ocr_service import extract_text
from app.services.ingredient_service import analyze_ingredients

router = APIRouter(prefix="/analyze", tags=["Full Analysis"])


@router.post("/image")
async def analyze_food_label(file: UploadFile = File(...)):
    """Run OCR and ingredient recognition on one uploaded label."""

    try:
        image_bytes = await file.read()

        # Stage 1: Extract text from the uploaded image.
        ocr_result = extract_text(image_bytes)
        extracted_text = ocr_result["extracted_text"]

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text was detected. "
                    "Try a clearer, well-lit image of the ingredient label."
                ),
            )

        # Stage 2: Recognize ingredients and known additive codes.
        ingredient_result = analyze_ingredients(extracted_text)

        # Stage 3: Return one response for frontend integration.
        return {
            "success": True,
            "filename": file.filename,
            "analysis_status": (
                "review_required"
                if ingredient_result["review_required"]
                else "completed"
            ),
            "ocr": {
                "extracted_text": extracted_text,
                "character_count": len(extracted_text),
            },
            **ingredient_result,
            "limitations": [
                "OCR can misread or omit label text.",
                "Ingredient recognition is limited to the current reference list.",
                "Additive identification does not establish toxicity or health risk.",
                "Unrecognized terms require review.",
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()
