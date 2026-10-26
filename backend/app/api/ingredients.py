from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ingredient_service import analyze_ingredients

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


class IngredientAnalysisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)


@router.post("/analyze")
def analyze_label(request: IngredientAnalysisRequest):
    try:
        return analyze_ingredients(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc