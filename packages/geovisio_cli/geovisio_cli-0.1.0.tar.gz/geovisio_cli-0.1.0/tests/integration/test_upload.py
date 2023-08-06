import os
import pytest
from ..conftest import FIXTURE_DIR
from pathlib import Path
import requests
from geovisio_cli import sequence, exception, model
from datetime import timedelta
import re
import toml


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_valid_upload(geovisio, datafiles):
    uploadReport = sequence.upload(
        path=Path(datafiles), geovisio=geovisio, title="some title"
    )
    assert len(uploadReport.uploaded_pictures) == 3
    assert len(uploadReport.errors) == 0

    collection = sequence.Sequence(location=uploadReport.location)
    sequence.wait_for_sequence(collection, timeout=timedelta(minutes=1))
    status = sequence.status(collection)
    sequence_info = sequence.info(collection)
    # 3 pictures should have been uploaded
    assert len(status.pictures) == 3

    for i in status.pictures:
        assert i.status == "ready"

    # the collection should also have 3 items
    collection = requests.get(f"{collection.location}/items")
    collection.raise_for_status()

    features = collection.json()["features"]
    assert len(features) == 3

    assert sequence_info.title == "some title"
    assert sequence_info.interior_orientation == [
        sequence.InteriorOrientation(
            make="SONY", model="FDR-X1000V", field_of_view=None
        )
    ]

    # Check generated TOML file
    tomlFile = datafiles / sequence.SEQUENCE_TOML_FILE
    with open(tomlFile, "r") as f:
        tomlFileContent = f.read()
        seqToml = toml.loads(tomlFileContent)
        assert seqToml["sequence"]["id"] == sequence_info.id
        assert seqToml["pictures"]["e1.jpg"]["id"] == features[0]["id"]
        assert seqToml["pictures"]["e2.jpg"]["id"] == features[1]["id"]
        assert seqToml["pictures"]["e3.jpg"]["id"] == features[2]["id"]


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_resume_upload(geovisio, datafiles):
    # Make e2 not valid to have a partial upload
    picE2 = datafiles / "e2.jpg"
    picE2bak = datafiles / "e2.bak"
    os.rename(picE2, picE2bak)
    with open(picE2, "w") as picE2file:
        picE2file.write("")
        picE2file.close()

    # Start upload -> 2 uploaded pics + 1 failure
    uploadReport = sequence.upload(
        path=Path(datafiles), geovisio=geovisio, title="some title"
    )
    assert len(uploadReport.uploaded_pictures) == 2
    assert len(uploadReport.errors) == 1
    assert uploadReport.errors[0].position == 2

    # Check TOML file -> e2 has no ID but broken status
    tomlFile = datafiles / sequence.SEQUENCE_TOML_FILE
    with open(tomlFile, "r") as f:
        tomlFileContent = f.read()
        f.close()
        seqToml = toml.loads(tomlFileContent)
        assert seqToml["pictures"]["e2.jpg"].get("id") is None
        assert seqToml["pictures"]["e2.jpg"]["status"] == "broken"

    # Make e2 valid
    os.remove(picE2)
    os.rename(picE2bak, picE2)

    # Launch again upload : 1 uploaded pic + 0 failure
    uploadReport2 = sequence.upload(
        path=Path(datafiles), geovisio=geovisio, title="some title"
    )
    assert uploadReport2.location == uploadReport.location
    assert len(uploadReport2.uploaded_pictures) == 1
    assert len(uploadReport2.errors) == 0

    # Check TOML file -> everything has ID and looks like a charm
    with open(tomlFile, "r") as f:
        tomlFileContent = f.read()
        f.close()
        seqToml2 = toml.loads(tomlFileContent)
        assert seqToml2["sequence"]["id"] == seqToml["sequence"]["id"]
        assert (
            seqToml2["pictures"]["e1.jpg"]["id"] == seqToml["pictures"]["e1.jpg"]["id"]
        )
        assert seqToml2["pictures"]["e2.jpg"]["id"] is not None
        assert seqToml2["pictures"]["e2.jpg"].get("status") is None
        assert (
            seqToml2["pictures"]["e3.jpg"]["id"] == seqToml["pictures"]["e3.jpg"]["id"]
        )


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
    os.path.join(FIXTURE_DIR, "invalid_pic.jpg"),
)
def test_upload_with_invalid_file(geovisio, datafiles):
    uploadReport = sequence.upload(path=Path(datafiles), geovisio=geovisio, title=None)

    # Only 3 pictures should have been uploaded, 1 is in error
    assert len(uploadReport.uploaded_pictures) == 3
    assert len(uploadReport.errors) == 1

    # But the collection status should have 3 items (and be valid)
    collection = sequence.Sequence(location=uploadReport.location)
    sequence.wait_for_sequence(collection, timeout=timedelta(minutes=1))
    status = sequence.status(collection)
    # 3 pictures should have been uploaded
    assert len(status.pictures) == 3

    assert all([i.status == "ready" for i in status.pictures])

    # the collection should also have 3 items
    items = requests.get(f"{collection.location}/items")
    items.raise_for_status()
    features = items.json()["features"]
    assert len(features) == 3
    collection = requests.get(f"{collection.location}")
    assert (
        collection.json()["title"] == Path(datafiles).name
    )  # since no title has been set, the directory name has been choosen


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "invalid_pic.jpg"),
)
def test_upload_with_no_valid_file(geovisio, datafiles):
    uploadReport = sequence.upload(
        path=Path(datafiles), geovisio=geovisio, title="a title"
    )

    assert len(uploadReport.uploaded_pictures) == 0
    assert len(uploadReport.errors) == 1

    status = requests.get(f"{uploadReport.location}/geovisio_status")
    assert (
        status.status_code == 404
    )  # TODO: For the moment geovisio return a 404, we it should return a valid status response with the sequence status

    items = requests.get(f"{uploadReport.location}/items")
    items.raise_for_status()
    features = items.json()["features"]
    assert len(features) == 0


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_upload_on_invalid_url_host(datafiles):
    with pytest.raises(exception.CliException) as e:
        sequence.upload(
            path=Path(datafiles),
            geovisio=model.Geovisio(url="http://some_invalid_url"),
            title="some title",
        )
    msg = str(e.value)
    assert msg.startswith(
        """The API is not reachable. Please check error and used URL below, and retry later if the URL is correct.

[bold]Used URL:[/bold] http://some_invalid_url/api/collections
[bold]Error:[/bold]"""
    )
    assert "Failed to establish a new connection:" in msg


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_upload_on_invalid_url_path(geovisio, datafiles):
    with pytest.raises(exception.CliException) as e:
        sequence.upload(
            path=Path(datafiles),
            geovisio=model.Geovisio(url=geovisio.url + "/some_additional_path"),
            title=None,
        )
    msg = str(e.value)
    assert msg.startswith(
        f"""The API URL is not valid.

Note that your URL should be the API root (something like https://geovisio.fr, https://panoramax.ign.fr or any other geovisio instance).
Please make sure you gave the correct URL and retry.

[bold]Used URL:[/bold] {geovisio.url}/some_additional_path/api/collections
[bold]Error:[/bold]"""
    )


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_upload_on_invalid_url_schema(datafiles):
    with pytest.raises(exception.CliException) as e:
        sequence.upload(
            path=Path(datafiles),
            geovisio=model.Geovisio(url="a non valid url at all"),
            title=None,
        )
    assert str(e.value).startswith(
        """Error while connecting to the API. Please check error and used URL below

[bold]Used URL:[/bold] a non valid url at all/api/collections
[bold]Error:[/bold]"""
    )
