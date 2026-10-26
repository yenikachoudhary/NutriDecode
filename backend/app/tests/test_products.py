
import httpx
import pytest

from app.services.product_service import fetch_product_by_barcode


@pytest.mark.asyncio
async def test_rejects_invalid_barcode():
    with pytest.raises(ValueError):
        await fetch_product_by_barcode("abc123")


@pytest.mark.asyncio
async def test_returns_not_found_for_unknown_product(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"status": 0, "product": None}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        FakeClient,
    )

    result = await fetch_product_by_barcode("12345678")

    assert result["success"] is False
    assert result["found"] is False
    assert result["barcode"] == "12345678"


@pytest.mark.asyncio
async def test_returns_product_data(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "status": 1,
                "product": {
                    "code": "12345678",
                    "product_name": "Example Snack",
                    "ingredients_text": "Potato, oil, salt",
                    "nutriments": {
                        "sugars_100g": 2.5,
                        "salt_100g": 1.2,
                    },
                },
            }

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)

    result = await fetch_product_by_barcode("12345678")

    assert result["found"] is True
    assert result["product"]["name"] == "Example Snack"
    assert result["product"]["nutrition_per_100g"]["sugars_g"] == 2.5
    assert result["data_quality"]["nutrition_available"] is True
