"""Thin wrappers around filesystem operations used by asset/job storage."""
import json
from pathlib import Path
from typing import Any


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, default=str))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())
