import pytest

from libastoria import AstoriaClient, AsyncAstoriaClient


def test_typing() -> None:
    client = AstoriaClient()

    assert not client.process.data.running
    client.process.request("kill")

@pytest.mark.asyncio
async def test_async() -> None:
    client = AsyncAstoriaClient()
    count = 0
    async for log in client.logs.iter():
        count += 1
        assert log.message == "yeet"
    assert count == 1

    data = await client.process.get_data()
    assert not data.running

    await client.process.request("kill")