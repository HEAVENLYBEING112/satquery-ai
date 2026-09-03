"""Canonical, safe path helpers. No path arriving from a client is ever trusted
without passing through these helpers first."""
import re
from pathlib import Path

_FILENAME_RE = re.compile(r"^[\w\-. ]+$")


def sanitize_filename(filename: str) -> str:
    """Strip directory components and dangerous characters from a client filename."""
    name = Path(filename).name
    name = re.sub(r"[^\-\w\. ]", "_", name)
    name = re.sub(r"\.{2,}", ".", name)
    name = name.strip(". ")
    if not name:
        name = "upload.tif"
    return name[:255]


def is_safe_evidence_filename(filename: str) -> bool:
    """Reject anything that looks like path traversal or an absolute path."""
    if ".." in filename or "/" in filename or "\\" in filename:
        return False
    if not _FILENAME_RE.match(filename):
        return False
    return True


def resolve_within(base_dir: Path, filename: str) -> Path:
    """Resolve `filename` under `base_dir`, raising if it would escape."""
    base_dir = base_dir.resolve()
    candidate = (base_dir / filename).resolve()
    if not candidate.is_relative_to(base_dir):
        raise ValueError(f"Resolved path {candidate} escapes allowed directory {base_dir}")
    return candidate
