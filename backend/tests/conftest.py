import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest


@pytest.fixture()
def tmp_settings(tmp_path, monkeypatch):
    from app.config import Settings

    s = Settings(runtime_dir=tmp_path / "runtime")
    return s
