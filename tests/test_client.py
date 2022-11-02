"""Test the client can access the disk state."""
import responses

from libastoria import AstoriaClient


class TestDisks:
    """Test the client can access the disk state."""
    
    @responses.activate
    def test_get_disks(self) -> None:
        """Test it."""
        responses.get(
            "http://localhost:34421/v1/domains/disks",
            json={"disks": ["yeet"]},
            status=403,
        )
        client = AstoriaClient()
        assert client.disks.data.disks == ["yeet"]
