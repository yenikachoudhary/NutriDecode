/**
 * Centralized API client for NutriDecode AI backend.
 * Uses environment variable VITE_API_BASE_URL with graceful fallback.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Handle HTTP response and standardize error payloads.
 */
async function handleResponse(response) {
  if (response.ok) {
    return response.json();
  }

  let errorDetail = `Request failed with status ${response.status}`;
  try {
    const errorJson = await response.json();
    if (errorJson && errorJson.detail) {
      errorDetail = errorJson.detail;
    } else if (errorJson && errorJson.message) {
      errorDetail = errorJson.message;
    }
  } catch {
    // Non-JSON response
  }

  const error = new Error(errorDetail);
  error.status = response.status;
  throw error;
}

/**
 * Perform a fetch with configurable timeout.
 */
async function fetchWithTimeout(url, options = {}, timeoutMs = 25000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(id);
    return await handleResponse(response);
  } catch (err) {
    clearTimeout(id);
    if (err.name === 'AbortError') {
      const timeoutError = new Error('Request timed out. The server or external provider took too long to respond.');
      timeoutError.status = 504;
      throw timeoutError;
    }
    if (err.message && err.message.includes('Failed to fetch')) {
      const netError = new Error(`Cannot reach NutriDecode API at ${API_BASE}. Ensure the backend server is running.`);
      netError.status = 503;
      throw netError;
    }
    throw err;
  }
}

export const api = {
  getBaseUrl() {
    return API_BASE;
  },

  async checkHealth() {
    return fetchWithTimeout(`${API_BASE}/health`, { method: 'GET' }, 5000);
  },

  async analyzeImage(file) {
    if (!file) throw new Error('Please select an image file to analyze.');
    if (file.size > 8 * 1024 * 1024) {
      throw new Error('Image size exceeds 8 MB limit. Please upload a smaller photograph.');
    }

    const formData = new FormData();
    formData.append('file', file);

    return fetchWithTimeout(`${API_BASE}/analyze/image`, {
      method: 'POST',
      body: formData,
    }, 45000); // 45s timeout for OCR on larger photos
  },

  async analyzeText(text, productName = null) {
    if (!text || !text.trim()) {
      throw new Error('Please provide ingredient label text to analyze.');
    }

    return fetchWithTimeout(`${API_BASE}/analyze/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, product_name: productName }),
    }, 15000);
  },

  async lookupBarcode(barcode) {
    const cleaned = String(barcode).trim();
    if (!cleaned) throw new Error('Please enter a numeric barcode.');
    if (!/^\d{8,14}$/.test(cleaned)) {
      throw new Error('Barcode must contain between 8 and 14 digits.');
    }

    return fetchWithTimeout(`${API_BASE}/products/barcode/${encodeURIComponent(cleaned)}`, {
      method: 'GET',
    }, 15000);
  },

  async resolveIndianName(name) {
    const cleaned = String(name).trim();
    if (!cleaned) throw new Error('Please enter an ingredient name.');
    return fetchWithTimeout(`${API_BASE}/ingredients/resolve-name?name=${encodeURIComponent(cleaned)}`, {
      method: 'GET',
    }, 10000);
  },

  async listEvidence() {
    return fetchWithTimeout(`${API_BASE}/evidence`, { method: 'GET' }, 10000);
  },

  async getAdditiveEvidence(code) {
    const cleaned = String(code).trim();
    return fetchWithTimeout(`${API_BASE}/evidence/${encodeURIComponent(cleaned)}`, { method: 'GET' }, 10000);
  },

  async calculateExposure({ concentration, servingSize, bodyWeight, adi, servingsPerDay = 1.0, additiveCode = null }) {
    return fetchWithTimeout(`${API_BASE}/exposure/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        concentration_mg_per_kg_food: Number(concentration),
        serving_size_g: Number(servingSize),
        body_weight_kg: Number(bodyWeight),
        adi_mg_per_kg_body_weight_day: Number(adi),
        servings_per_day: Number(servingsPerDay),
        additive_code: additiveCode,
      }),
    }, 10000);
  },

  async getReferenceAdi(code) {
    const cleaned = String(code).trim();
    return fetchWithTimeout(`${API_BASE}/exposure/reference-adi/${encodeURIComponent(cleaned)}`, {
      method: 'GET',
    }, 10000);
  },

  async listReferenceAdis() {
    return fetchWithTimeout(`${API_BASE}/exposure/reference-adis`, {
      method: 'GET',
    }, 10000);
  },

  async generateAiSummary(analysisResult, preferences = null, providerOverride = null) {
    if (!analysisResult) throw new Error('Analysis result payload is required to generate AI summary.');

    return fetchWithTimeout(`${API_BASE}/analyze/ai-summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        analysis_result: analysisResult,
        preferences: preferences || undefined,
        provider_override: providerOverride || undefined,
      }),
    }, 35000); // 35s timeout for LLM generation
  },

  async searchProducts(query, limit = 5) {
    const cleaned = String(query || '').trim();
    if (!cleaned) throw new Error('Please enter a product title or keyword to search.');

    return fetchWithTimeout(`${API_BASE}/products/search?query=${encodeURIComponent(cleaned)}&limit=${limit}`, {
      method: 'GET',
    }, 15000);
  },
};
