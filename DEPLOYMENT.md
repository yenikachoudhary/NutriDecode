# NutriDecode AI — Complete Deployment Guide (Beginner & Student Friendly)

This guide provides step-by-step instructions to deploy the NutriDecode AI full-stack application (FastAPI backend + React Vite frontend) using beginner-friendly, free-tier hosting platforms (such as **Render**, **Railway**, and **Vercel**).

No credit card is required for basic free-tier hosting on Render or Vercel.

---

## 1. Pre-Deployment Checklist

Before deploying:
- [x] All 50 automated backend tests pass (`pytest`).
- [x] Frontend builds cleanly without errors (`npm run build`).
- [x] Backend Dockerfile includes `tesseract-ocr` and OpenCV runtime dependencies.
- [x] `.env.example` templates exist for both backend and frontend.
- [x] AI summary service operates with live Gemini LLM or deterministic grounded fallback when no key is set.
- [x] Private credentials and virtual environments are excluded via `.gitignore`.
- [x] CORS configuration dynamically accepts production frontend domains.

---

## 2. Recommended Free Deployment Architecture

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     Vercel or Render Static     │       │    Render or Railway (Docker)   │
│         (React Frontend)        │──────▶│        (FastAPI Backend)        │
│  https://nutridecode.vercel.app │ HTTPS │ https://nutridecode.onrender.com│
└─────────────────────────────────┘       └─────────────────────────────────┘
```

---

## 3. Step-by-Step Deployment Guide

### Option A: Deploying with Render (Simplest Single Dashboard)

Render supports both Docker Web Services (for the backend with Tesseract) and Static Sites (for the Vite frontend) for free.

#### Step 1: Push your project to GitHub
1. Open your terminal in `NutriDecode/`.
2. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: complete full-stack prototype with ocr, evidence, and exposure"
   git push origin main
   ```

#### Step 2: Deploy the Backend on Render
1. Go to [render.com](https://render.com) and sign in with GitHub.
2. Click **New +** → **Web Service**.
3. Select your GitHub repository `NutriDecode`.
4. Configure the Web Service:
   - **Name:** `nutridecode-backend`
   - **Region:** Singapore or Frankfurt (choose the closest to your users)
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Docker` (Render will automatically detect `backend/Dockerfile` and install Tesseract)
   - **Instance Type:** `Free`
5. Under **Environment Variables**, add:
   - `APP_NAME` = `NutriDecode API`
   - `APP_ENV` = `production`
   - `API_V1_PREFIX` = `/api/v1`
   - `FRONTEND_ORIGINS` = `http://localhost:5173,https://<your-frontend-subdomain>.vercel.app,https://<your-frontend-subdomain>.onrender.com`
   - *(Optional for Live LLM)* `AI_PROVIDER` = `gemini` (defaults to deterministic grounded fallback if unset)
   - *(Optional for Live LLM)* `GEMINI_API_KEY` = `<your-google-gemini-api-key>` (obtain free key from [aistudio.google.com](https://aistudio.google.com))
   - *(Optional for Live LLM)* `GEMINI_MODEL` = `gemini-1.5-flash`
6. Click **Create Web Service**.
7. Wait 3–4 minutes for the Docker image to build. Once complete, copy your public backend URL (e.g., `https://nutridecode-backend.onrender.com`).
8. Verify in your browser: Visit `https://nutridecode-backend.onrender.com/api/v1/health`. It should return:
   ```json
   {"status":"ok","app":"NutriDecode API","version":"0.1.0","environment":"production"}
   ```

#### Step 3: Deploy the Frontend on Vercel or Render
##### If using Vercel (Fastest & Free CDN):
1. Go to [vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New...** → **Project** and import your `NutriDecode` repository.
3. Configure the project:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click Edit and select `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Expand **Environment Variables** and add:
   - `VITE_API_BASE_URL` = `https://nutridecode-backend.onrender.com/api/v1` *(use your actual backend URL from Step 2)*
5. Click **Deploy**.
6. After ~45 seconds, your site is live!

##### If using Render Static Site:
1. On Render dashboard, click **New +** → **Static Site**.
2. Select repository `NutriDecode`.
3. Root Directory: `frontend`
4. Build Command: `npm install && npm run build`
5. Publish Directory: `dist`
6. Environment Variables:
   - `VITE_API_BASE_URL` = `https://nutridecode-backend.onrender.com/api/v1`
7. Click **Create Static Site**.

#### Step 4: Update Backend CORS with your Frontend Domain
1. In your Render backend dashboard, go to **Environment**.
2. Update `FRONTEND_ORIGINS` to include your new frontend URL:
   ```
   http://localhost:5173,https://your-frontend-app.vercel.app
   ```
3. Save changes. Render will automatically redeploy the backend with the new allowed origin.

---

## 4. Post-Deployment Smoke Test Checklist

Once both services are deployed, test the live website in your browser:

- [ ] **1. Health Pill:** In the top header navigation, verify the green pill displays **"API Active"**.
- [ ] **2. Barcode Search & Discovery:** Navigate to **Barcode Lookup**, search sample `3017620422003`. Also test "Unknown-Product Discovery" by typing `Parle-G` and confirming candidate cards with completeness % indicators render properly.
- [ ] **3. Photo / Text Scanner & AI Summary:** Navigate to **Label Scanner**, analyze a sample, and click **"Generate AI Summary"**. Confirm that the structured summary renders with transparent grounding badges, dietary alignment, and source links.
- [ ] **4. Personalization Controls:** Click **"Personalize"**, select "Vegan" or flag "Palm oil", and verify that the summary immediately highlights matching exclusions without inventing concentrations.
- [ ] **5. Evidence Database:** Navigate to **Evidence Database**, search for `330` or `150d`, and expand the card to verify the JECFA monograph and FSSAI PDF links open correctly in new tabs.
- [ ] **6. Exposure Simulator:** Navigate to **Exposure Calculator**, select `INS 211 — Sodium benzoate`, adjust serving size to 100g, and verify the ADI percentage and scientific interpretation compute immediately. Select `INS 330 — Citric acid` and verify the GMP discovery guidance appears.

---

## 5. Rollback & Recovery Plan

- **Free-tier sleep mode:** On Render free web services, inactive servers sleep after 15 minutes of inactivity. The first request after a sleep period may take 30–45 seconds to spin up. The frontend shows a friendly "Connecting to API..." status during this warm-up.
- **Rollback in Render:** If a code deployment fails, go to Render Dashboard → **Deploys** → click the three dots next to the previous successful deploy → select **Rollback to this deploy**.
- **Rollback in Vercel:** Go to Vercel Dashboard → **Deployments** → select previous deployment → click **Instant Rollback**.
