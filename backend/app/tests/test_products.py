import httpx
import pytest

from app.services.product_service import fetch_product_by_barcode, clear_cache


@pytest.fixture(autouse=True)
def clean_product_cache():
    clear_cache()
    yield
    clear_cache()


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.text = ""

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request(
                "GET", "https://example.com/test"
            )
            response = httpx.Response(
                self.status_code,
                request=request,
                text=self.text,
            )
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=request,
                response=response,
            )

    def json(self):
        return self.payload


class FakeClient:
    """Async HTTP client mock with queued responses."""

    def __init__(self, *args, **kwargs):
        self.responses = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, *args, **kwargs):
        if not self.responses:
            raise AssertionError("No mocked response configured")
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_rejects_invalid_barcode():
    with pytest.raises(ValueError):
        await fetch_product_by_barcode("abc123")


@pytest.mark.asyncio
async def test_returns_not_found_for_unknown_product(monkeypatch):
    responses = [
        FakeResponse({"status": 0, "product": None}),
        FakeResponse({"code": "OK", "items": []}),
    ]

    class MockClient(FakeClient):
        async def get(self, *args, **kwargs):
            return responses.pop(0)

    monkeypatch.setattr(httpx, "AsyncClient", MockClient)

    result = await fetch_product_by_barcode("12345678")

    assert result["success"] is False
    assert result["found"] is False
    assert result["barcode"] == "12345678"
    assert "UPCitemdb" in result["sources_checked"]


@pytest.mark.asyncio
async def test_returns_product_data(monkeypatch):
    responses = [
        FakeResponse({
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
        })
    ]

    class MockClient(FakeClient):
        async def get(self, *args, **kwargs):
            return responses.pop(0)

    monkeypatch.setattr(httpx, "AsyncClient", MockClient)

    result = await fetch_product_by_barcode("12345678")

    assert result["found"] is True
    assert result["product"]["name"] == "Example Snack"
    assert result["product"]["nutrition_per_100g"]["sugars_g"] == 2.5
    assert result["data_quality"]["nutrition_available"] is True


@pytest.mark.asyncio
async def test_uses_upcitemdb_when_open_food_facts_returns_404(
    monkeypatch,
):
    responses = [
        FakeResponse({}, status_code=404),
        FakeResponse({
            "code": "OK",
            "items": [{
                "ean": "12345678",
                "title": "Fallback Snack",
                "brand": "Example Brand",
                "images": [],
            }],
        }),
    ]

    class MockClient(FakeClient):
        async def get(self, *args, **kwargs):
            return responses.pop(0)

    monkeypatch.setattr(httpx, "AsyncClient", MockClient)

    result = await fetch_product_by_barcode("12345678")

    assert result["success"] is True
    assert result["found"] is True
    assert result["data_source"] == "UPCitemdb"
    assert result["product"]["name"] == "Fallback Snack"
    assert result["data_quality"]["ingredients_available"] is False


@pytest.mark.asyncio
async def test_serves_repeated_lookup_from_cache(monkeypatch):
    responses = [
        FakeResponse({
            "status": 1,
            "product": {
                "code": "99998888",
                "product_name": "Cached Snack",
                "nutriments": {"sugars_100g": 1.0},
            },
        })
    ]

    class MockClient(FakeClient):
        async def get(self, *args, **kwargs):
            return responses.pop(0)

    monkeypatch.setattr(httpx, "AsyncClient", MockClient)

    first = await fetch_product_by_barcode("99998888")
    assert first["found"] is True
    assert first["product"]["name"] == "Cached Snack"

    # Second lookup should come from cache without calling MockClient.get
    second = await fetch_product_by_barcode("99998888")
    assert second["found"] is True
    assert second["from_cache"] is True
