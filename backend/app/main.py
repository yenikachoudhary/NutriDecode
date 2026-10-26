
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.core.config import get_settings

from app.api.ocr import router as ocr_router
from app.api.ingredients import router as ingredients_router
from app.api.analyze import router as analyze_router


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Evidence-based food ingredient analysis and "
        "consumer safety research platform."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(
    health_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    ocr_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    ingredients_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    analyze_router,
    prefix=settings.api_v1_prefix,
)

@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    """Provide basic API information."""

    return {
        "message": "Welcome to NutriDecode API",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
