"""Configurable AI Provider Abstraction for NutriDecode.

Supports Google Gemini (via official REST API with JSON schema mode),
OpenAI-compatible APIs, and a deterministic Mock provider for offline testing.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    """Base exception for AI provider failures."""


class AIAuthenticationError(AIProviderError):
    """Raised when the AI provider rejects credentials (HTTP 401/403)."""


class AIRateLimitError(AIProviderError):
    """Raised when the AI provider rate limit is exceeded (HTTP 429)."""


class AITimeoutError(AIProviderError):
    """Raised when the AI provider times out."""


class AIResponseValidationError(AIProviderError):
    """Raised when the AI output does not conform to the expected schema."""


class AIProviderNotConfiguredError(AIProviderError):
    """Raised when an AI operation is requested but no provider/key is configured."""


class BaseAIProvider(ABC):
    """Abstract base class for all AI summary providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the lowercase identifier of the provider."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the active model name."""

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_instruction: str,
        timeout_seconds: float = 25.0,
    ) -> dict[str, Any]:
        """Generate structured JSON adhering to prompt specifications."""


class GeminiProvider(BaseAIProvider):
    """Official Google Gemini API provider using generateContent with JSON mode."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        if not api_key or not api_key.strip():
            raise AIProviderNotConfiguredError("Gemini API key is required.")
        self._api_key = api_key.strip()
        self._model = model.strip() or "gemini-2.5-flash"
        self._endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent"
        )

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_json(
        self,
        prompt: str,
        system_instruction: str,
        timeout_seconds: float = 25.0,
    ) -> dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self._api_key,
        }

        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1,  # Low temperature for strict factual adherence
                "maxOutputTokens": 3072,
            },
        }

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            try:
                response = await client.post(
                    self._endpoint,
                    json=payload,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                logger.warning("Gemini API request timed out: %s", exc)
                raise AITimeoutError("Gemini API timed out while generating summary.") from exc
            except httpx.RequestError as exc:
                logger.error("Gemini API connection error: %s", exc)
                raise AIProviderError(f"Network error connecting to Gemini API: {exc}") from exc

            if response.status_code in (401, 403):
                logger.error("Gemini API authentication rejected (HTTP %s)", response.status_code)
                raise AIAuthenticationError("Invalid or unauthorized Gemini API key.")

            if response.status_code == 429:
                logger.warning("Gemini API rate limit reached (HTTP 429)")
                raise AIRateLimitError("Gemini rate limit exceeded. Please try again shortly.")

            if response.status_code >= 400:
                logger.error("Gemini API returned error HTTP %s: %s", response.status_code, response.text[:400])
                raise AIProviderError(f"Gemini API error (HTTP {response.status_code})")

            try:
                data = response.json()
                candidates = data.get("candidates") or []
                if not candidates:
                    raise AIResponseValidationError("Gemini returned empty candidate response.")

                parts = candidates[0].get("content", {}).get("parts") or []
                if not parts:
                    raise AIResponseValidationError("No content parts in Gemini candidate.")

                raw_text = parts[0].get("text", "").strip()
                # Parse JSON
                return json.loads(raw_text)
            except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
                logger.error("Failed to parse Gemini response as JSON: %s", exc)
                raise AIResponseValidationError(f"Gemini output was not valid JSON: {exc}") from exc


class OpenAICompatibleProvider(BaseAIProvider):
    """OpenAI-compatible chat completion provider."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
    ):
        if not api_key or not api_key.strip():
            raise AIProviderNotConfiguredError("OpenAI API key is required.")
        self._api_key = api_key.strip()
        self._model = model.strip() or "gpt-4o-mini"
        self._base_url = base_url.rstrip("/")

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_json(
        self,
        prompt: str,
        system_instruction: str,
        timeout_seconds: float = 25.0,
    ) -> dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 3072,
        }

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            try:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                raise AITimeoutError("OpenAI API timed out.") from exc
            except httpx.RequestError as exc:
                raise AIProviderError(f"OpenAI connection error: {exc}") from exc

            if response.status_code in (401, 403):
                raise AIAuthenticationError("Invalid OpenAI credentials.")
            if response.status_code == 429:
                raise AIRateLimitError("OpenAI rate limit reached.")
            if response.status_code >= 400:
                raise AIProviderError(f"OpenAI error (HTTP {response.status_code})")

            try:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
            except Exception as exc:
                raise AIResponseValidationError(f"Invalid OpenAI JSON payload: {exc}") from exc


class MockAIProvider(BaseAIProvider):
    """Deterministic, mock provider for offline testing and continuous integration.

    Produces grounded, structured summaries directly from the provided evidence.
    """

    def __init__(self, model: str = "mock-grounded-v1", mock_response: dict[str, Any] | None = None):
        self._model = model
        self._mock_response = mock_response

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_json(
        self,
        prompt: str,
        system_instruction: str,
        timeout_seconds: float = 5.0,
    ) -> dict[str, Any]:
        if self._mock_response is not None:
            return self._mock_response

        # Return a deterministic, schema-compliant dictionary
        return {
            "product_overview": (
                "Packaged food sample analyzed with NutriDecode. "
                "Ingredients include recognized grain/oil bases and authorized food additives."
            ),
            "nutritional_observations": [
                "Nutrient values reflect the available manufacturer panel.",
                "Sugar, saturated fat, and sodium evaluated against experimental thresholds.",
            ],
            "ingredient_and_additive_explanations": [
                {
                    "name": "Identified Ingredients",
                    "purpose": "Food matrix and stabilization",
                    "scientific_findings": "Evaluated in accordance with FSSAI regulations.",
                    "evidence_status": "verified_evidence",
                    "source_name": "FSSAI & JECFA",
                    "source_url": "https://fssai.gov.in/",
                }
            ],
            "health_effects": {
                "short_term_effects": "No acute toxicity indicated at standard food intake levels.",
                "long_term_effects": "No evidence of cumulative toxicity when consumed within Good Manufacturing Practice.",
                "excessive_exposure_effects": "Excessive intake of sodium or saturated fat may contribute to cardiovascular concerns.",
                "sensitivities_and_allergens": "Inspect declared allergens carefully. Individuals with sensitivities should review label.",
            },
            "exposure_assessment": {
                "status": "not_calculable_from_label",
                "explanation": (
                    "Exact additive concentrations are not declared on retail packages. "
                    "Use the Dietary Exposure Calculator tool to test specific intake scenarios against JECFA ADIs."
                ),
                "reference_adi": "Refer to JECFA monograph thresholds",
            },
            "allergen_and_dietary_alignment": [
                {
                    "preference_or_allergen": "General Safety & Accuracy",
                    "status": "matches",
                    "explanation": "Evaluated against declared ingredients on the package.",
                }
            ],
            "missing_or_uncertain_information": [
                "Exact concentrations of additives are not declared on the package.",
                "Unrecognized terms require citizen-science human review.",
            ],
            "consumer_next_steps": [
                "Verify allergen information on the physical package.",
                "Compare serving size with your personal daily intake.",
                "Consult healthcare professionals for personal medical or dietary conditions.",
            ],
            "source_references": [
                {
                    "organization": "WHO/FAO JECFA",
                    "title": "Joint FAO/WHO Expert Committee on Food Additives Monograph Database",
                    "url": "https://apps.who.int/food-additives-contaminants-jecfa-database/",
                },
                {
                    "organization": "FSSAI",
                    "title": "Food Safety and Standards (Food Products Standards and Food Additives) Regulations",
                    "url": "https://fssai.gov.in/",
                },
            ],
            "grounding_statement": (
                "This summary was generated from verified label data and authoritative regulatory sources. "
                "It is not a medical diagnosis or absolute guarantee of safety."
            ),
        }


def get_ai_provider(provider_override: str | None = None) -> BaseAIProvider | None:
    """Factory to instantiate the appropriate AI provider based on configuration."""
    settings = get_settings()
    choice = (provider_override or settings.ai_provider or "auto").lower().strip()

    if choice == "disabled":
        return None

    if choice == "mock":
        return MockAIProvider()

    # If explicitly requested or auto-detect Gemini
    if choice in ("gemini", "auto") and settings.gemini_api_key:
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    # If explicitly requested or auto-detect OpenAI
    if choice in ("openai", "auto") and settings.openai_api_key:
        return OpenAICompatibleProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_api_base,
        )

    # If auto was chosen but no key configured, return None
    return None
