from pathlib import Path

import pytest

from app.services.asset_service import ApiError
from app.services.evidence_service import resolve_evidence_path
from app.storage.paths import is_safe_evidence_filename, sanitize_filename


def test_sanitize_filename_strips_traversal():
    assert sanitize_filename("../../evil.tif") == "evil.tif"


def test_sanitize_filename_strips_bad_chars():
    assert sanitize_filename('weird<>:"|?*name.tif') == "weird_______name.tif"


def test_sanitize_filename_empty_falls_back():
    assert sanitize_filename("") == "upload.tif"
    assert sanitize_filename("...") == "upload.tif"


@pytest.mark.parametrize(
    "name,expected",
    [
        ("../etc/passwd", False),
        ("../../secret", False),
        ("a/b.png", False),
        ("a\\b.png", False),
        ("valid.png", True),
        ("valid_name-1.png", True),
    ],
)
def test_is_safe_evidence_filename(name, expected):
    assert is_safe_evidence_filename(name) is expected


def test_resolve_evidence_path_rejects_traversal(tmp_path):
    jobs_dir = tmp_path / "jobs"
    job_dir = jobs_dir / "job1" / "output"
    job_dir.mkdir(parents=True)
    (job_dir / "valid.png").write_bytes(b"fake")

    with pytest.raises(ApiError) as exc:
        resolve_evidence_path(jobs_dir, "job1", "../../../etc/passwd")
    assert exc.value.code == "INVALID_FILENAME"


def test_resolve_evidence_path_success(tmp_path):
    jobs_dir = tmp_path / "jobs"
    job_dir = jobs_dir / "job1" / "output"
    job_dir.mkdir(parents=True)
    target = job_dir / "valid.png"
    target.write_bytes(b"fake")

    result = resolve_evidence_path(jobs_dir, "job1", "valid.png")
    assert result == target.resolve()


def test_resolve_evidence_path_missing(tmp_path):
    jobs_dir = tmp_path / "jobs"
    (jobs_dir / "job1" / "output").mkdir(parents=True)

    with pytest.raises(ApiError) as exc:
        resolve_evidence_path(jobs_dir, "job1", "missing.png")
    assert exc.value.code == "EVIDENCE_NOT_FOUND"


def test_all_expected_extensions_allowed():
    from app.config import Settings

    s = Settings()
    for ext in (".tif", ".tiff", ".png", ".jpg", ".jpeg"):
        assert ext in s.allowed_extensions


def test_format_by_extension_covers_all_allowed():
    from app.config import Settings
    from app.services.asset_service import FORMAT_BY_EXTENSION

    s = Settings()
    for ext in s.allowed_extensions:
        assert ext in FORMAT_BY_EXTENSION, f"{ext} allowed but has no format mapping"


def test_format_by_extension_values():
    from app.services.asset_service import FORMAT_BY_EXTENSION

    assert FORMAT_BY_EXTENSION[".tif"] == "GeoTIFF"
    assert FORMAT_BY_EXTENSION[".tiff"] == "GeoTIFF"
    assert FORMAT_BY_EXTENSION[".png"] == "PNG"
    assert FORMAT_BY_EXTENSION[".jpg"] == "JPEG"
    assert FORMAT_BY_EXTENSION[".jpeg"] == "JPEG"
