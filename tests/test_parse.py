from pathlib import Path

import pytest

from split_cue import parse_cue, safe, unquote

CUE = '''REM GENRE "Alternative"
REM DATE 2001
PERFORMER "Muse"
TITLE "Origin of Symmetry"
FILE "album.flac" WAVE
  TRACK 01 AUDIO
    TITLE "New Born"
    PERFORMER "Muse"
    INDEX 01 00:00:00
  TRACK 02 AUDIO
    TITLE "Bliss"
    INDEX 01 06:03:37
'''


@pytest.fixture
def cue_file(tmp_path: Path) -> Path:
    p = tmp_path / "album.cue"
    p.write_text(CUE, encoding="utf-8")
    return p


def test_album_tags(cue_file):
    album, _ = parse_cue(cue_file)
    assert album["performer"] == "Muse"
    assert album["title"] == "Origin of Symmetry"
    assert album["date"] == "2001"
    assert album["genre"] == "Alternative"
    assert album["files"] == ["album.flac"]


def test_tracks_and_timing(cue_file):
    _, tracks = parse_cue(cue_file)
    assert [t["num"] for t in tracks] == [1, 2]
    assert tracks[0]["start"] == 0
    assert tracks[1]["start"] == pytest.approx(363 + 37 / 75)
    assert tracks[1]["title"] == "Bliss"


def test_cp1251_encoding(tmp_path):
    p = tmp_path / "a.cue"
    p.write_bytes('PERFORMER "Кино"\nTITLE "Группа крови"\n'.encode("cp1251"))
    album, _ = parse_cue(p)
    assert album["performer"] == "Кино"


def test_safe_filename():
    assert safe('AC/DC: "Back in Black"?') == "AC_DC_ _Back in Black__"
    assert safe("...") == "_"


def test_unquote():
    assert unquote('"a b.flac" WAVE') == "a b.flac"
    assert unquote("2001") == "2001"
