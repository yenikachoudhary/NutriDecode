
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.ocr_service import extract_text
from app.services.ingredient_service import analyze_ingredients
from app.services.evidence_service import get_additive_evidence

router = APIRouter(prefix="/analyze", tags=["Full Analysis"])


@router.post("/image")
async def analyze_food_label(file: UploadFile = File(...)):
    """Extract label text, recognize ingredients and attach evidence."""

    try:
        image_bytes = await file.read()

        # Stage 1: Extract text from the image.
        ocr_result = extract_text(image_bytes)
        extracted_text = ocr_result["extracted_text"]

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text was detected. Try a clearer image "
                    "of the ingredient label."
                ),
            )

        # Stage 2: Recognize ingredients and additive codes.
        ingredient_result = analyze_ingredients(extracted_text)

        # Stage 3: Attach source-linked evidence to each known additive.
        enriched_additives = []

        for additive in ingredient_result.get("additives", []):
            evidence = get_additive_evidence(additive["code"])

            enriched_additives.append({
                **additive,
                "evidence_status": (
                    evidence["evidence_status"]
                    if evidence
                    else "not_in_catalogue"
                ),
                "evidence": evidence,
            })

        ingredient_result["additives"] = enriched_additives

        # Stage 4: Return one response for the frontend.
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
                "Source links are reference starting points, not proof of "
                "individual scientific verification.",
                "Additive identification does not establish toxicity "
                "or personal health risk.",
                "Unrecognized terms require review.",
            ],
        }

    except HTTPException:
        raise

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
