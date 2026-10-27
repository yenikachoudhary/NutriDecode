# NutriDecode API

Backend for NutriDecode AI, an evidence-based food ingredient analysis, Indian regional alias resolution, and consumer safety research platform.

## Requirements

- Python 3.11 or newer
- pip
- Tesseract-OCR (v5+)

## Setup

Create and activate a virtual environment:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create `.env` using `.env.example`:

```powershell
Copy-Item .env.example .env
```

## Running the API

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

- API root: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/api/v1/health`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- Redoc Documentation: `http://127.0.0.1:8000/redoc`

## Running Automated Tests

Run all 40 automated pytest unit and integration tests:

```powershell
python -m pytest -v
```

## API Modules

- `app/api/health.py`: Process health and environment check.
- `app/api/ocr.py`: Image validation, CLAHE preprocessing, and Tesseract OCR.
- `app/api/ingredients.py`: Ingredient parsing, additive regex extraction, and Indian alias resolution.
- `app/api/analyze.py`: Combined multimodal image analysis and direct text re-analysis pipeline.
- `app/api/evidence.py`: WHO/FAO JECFA chemical evaluations and FSSAI regulatory standards.
- `app/api/exposure.py`: Quantitative dietary exposure calculator and ADI threshold simulator.
- `app/api/products.py`: Barcode lookup querying Open Food Facts v2 with UPCitemdb fallback and in-memory TTL caching.
