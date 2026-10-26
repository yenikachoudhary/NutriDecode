
# NutriDecode API

Backend for NutriDecode 2.0, an evidence-based food ingredient
analysis and consumer safety research platform.

## Requirements

- Python 3.11 or newer
- pip
- Git

## Setup

Create and activate a virtual environment from this directory.

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create `.env` using `.env.example` as a template.

## Run the API

```powershell
python -m uvicorn app.main:app --reload
```

The development server runs at:

- API root: http://127.0.0.1:8000/
- Health: http://127.0.0.1:8000/api/v1/health
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Run tests

```powershell
python -m pytest -v
```

## Current scope

- FastAPI application foundation
- Environment-based configuration
- CORS configuration for local frontend development
- Root and health-check endpoints
- Automated API tests

OCR, ingredient intelligence, evidence retrieval, and interaction
analysis will be implemented as separate modules.
