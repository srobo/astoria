"""Smoke tests for libastoria typing."""
import pytest

from libastoria import AsyncAstoriaClient


@pytest.mark.asyncio
async def test_async() -> None:
    """Smoke test for async client."""
    client = AsyncAstoriaClient()
    count = 0
    async for log in client.logs.iter():
        count += 1
        assert log.message == "yeet"
    assert count == 1
