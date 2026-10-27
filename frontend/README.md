# NutriDecode Frontend

Modern React 18 single-page application built with Vite and Tailwind CSS for the NutriDecode AI consumer food safety platform.

## Features

- **Food Label Workspace:** Drag-and-drop photo upload with image preview, Tesseract OCR text extraction, in-place text editor for misread labels, ingredient tagger, and additive evidence viewer.
- **Indian Regional Name Resolution:** Automatically resolves colloquial Hindi, Tamil, Telugu, and Marathi ingredient aliases (e.g. *haldi*, *maida*, *uppu*, *methi*, *besan*) to canonical names.
- **Barcode Lookup:** Queries Open Food Facts and UPCitemdb for instant product packaging, nutrition table, and allergen information.
- **Dietary Exposure Calculator:** Interactive simulator comparing additive intake against authoritative WHO/FAO JECFA Acceptable Daily Intake (ADI) thresholds.
- **Verified Additive Catalogue:** Searchable database with direct source links to WHO/FAO JECFA monographs and official FSSAI schedules.
- **Citizen Science Portal:** Full Anveshana 2026 Student Science & Engineering Exhibition dossier connecting People, Machines, and the Planet.

## Setup & Running

Install dependencies:

```powershell
cd frontend
npm install
```

Configure `.env` using `.env.example`:

```ini
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Start Vite development server:

```powershell
npm run dev
```

Build for production:

```powershell
npm run build
```

Preview production build:

```powershell
npm run preview
```
