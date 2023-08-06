import pytest
from geovisio_cli import sequence, exception


def test_status_on_unknown_collection(geovisio):
    with pytest.raises(exception.CliException) as e:
        sequence.status(
            sequence.Sequence(location=f"{geovisio.url}/api/collections/some_bad_id")
        )
    assert e.match(f"Sequence {geovisio.url}/api/collections/some_bad_id not found")
