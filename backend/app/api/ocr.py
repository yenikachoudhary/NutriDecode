
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.ocr_service import extract_text

router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post("/extract")
async def extract_label_text(
    file: UploadFile = File(...),
):
    try:
        image_bytes = await file.read()
        result = extract_text(image_bytes)

        return {
            "filename": file.filename,
            **result,
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
