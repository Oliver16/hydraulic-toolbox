from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

UPLOAD_ROOT = Path("data/uploads")
EXPORT_ROOT = Path("data/exports")

UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
EXPORT_ROOT.mkdir(parents=True, exist_ok=True)


def save_upload(filename: str, content: bytes) -> Path:
    path = UPLOAD_ROOT / filename
    path.write_bytes(content)
    return path


def save_json(filename: str, payload: Dict[str, Any]) -> Path:
    path = EXPORT_ROOT / filename
    path.write_text(json.dumps(payload, indent=2))
    return path

