import pytest
import os
from geovisio_cli import sequence


@pytest.mark.parametrize(
    ("data", "expected"),
    (
        (["1.jpg", "2.jpg", "3.jpg"], ["1.jpg", "2.jpg", "3.jpg"]),
        (["3.jpg", "1.jpg", "2.jpg"], ["1.jpg", "2.jpg", "3.jpg"]),
        (["3.jpg", "1.jpg", "2.jpeg"], ["1.jpg", "2.jpeg", "3.jpg"]),
        (["10.jpg", "5.jpg", "1.jpg"], ["1.jpg", "5.jpg", "10.jpg"]),
        (["C.jpg", "A.jpg", "B.jpg"], ["A.jpg", "B.jpg", "C.jpg"]),
        (
            ["CAM1_001.jpg", "CAM2_002.jpg", "CAM1_002.jpg"],
            ["CAM1_001.jpg", "CAM1_002.jpg", "CAM2_002.jpg"],
        ),
    ),
)
def test_sort_files(data, expected):
    dataPictures = [sequence.Picture(path=p) for p in data]
    resPictures = sequence._sort_files(dataPictures)
    assert expected == [pic.path for pic in resPictures]


def test_rw_sequence_toml(tmp_path):
    s = sequence.Sequence(
        title="SEQUENCE",
        id="blab-blabla-blablabla",
        path=str(tmp_path),
        pictures=[
            sequence.Picture(
                id="blou-bloublou-bloubloublou-1", path=str(tmp_path / "1.jpg")
            ),
            sequence.Picture(
                id="blou-bloublou-bloubloublou-2", path=str(tmp_path / "2.jpg")
            ),
            sequence.Picture(
                id="blou-bloublou-bloubloublou-3", path=str(tmp_path / "3.jpg")
            ),
        ],
    )
    res = sequence._write_sequence_toml(s)
    assert res == str(tmp_path / "_geovisio.toml")
    res2 = sequence._update_sequence_from_toml(sequence.Sequence(path=str(tmp_path)))
    assert s == res2


def test_read_sequence(tmp_path):
    # First read : position is based on picture names
    pic1 = tmp_path / "1.jpg"
    open(pic1, "w").write("")
    pic2 = tmp_path / "2.jpg"
    open(pic2, "w").write("")
    seq = sequence._read_sequence(tmp_path)
    seqTomlPath = sequence._write_sequence_toml(seq)

    assert os.path.isfile(seqTomlPath)

    # Edit TOML file : position is inverted
    with open(seqTomlPath, "r+") as seqToml:
        editedSeqToml = seqToml.read()
        editedSeqToml = (
            editedSeqToml.replace("position = 1", "position = A")
            .replace("position = 2", "position = 1")
            .replace("position = A", "position = 2")
        )
        seqToml.seek(0)
        seqToml.write(editedSeqToml)
        seqToml.close()

        # Read sequence 2 : position should match edited TOML
        seq = sequence._read_sequence(tmp_path)
        assert seq.pictures[0].path.endswith("2.jpg")
        assert seq.pictures[1].path.endswith("1.jpg")
