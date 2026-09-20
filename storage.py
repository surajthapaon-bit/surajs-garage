"""Safe attachment storage — controlled directory, unique names, validation."""
from __future__ import annotations

import re
import uuid
from pathlib import Path

from config import ATTACHMENTS_DIR, CONFIG

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")
ALLOWED_EXT = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif",
    ".pdf", ".txt", ".csv", ".json", ".md",
}


def _safe_name(name: str) -> str:
    base = Path(name).name
    cleaned = _SAFE.sub("_", base).strip("._") or "file"
    return cleaned[:120]


def case_dir(case_number: str) -> Path:
    p = ATTACHMENTS_DIR / case_number
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_upload(case_number: str, uploaded) -> tuple[str, str, int, str | None]:
    """
    Persist an uploaded file.
    Returns (stored_name, original_name, size_bytes, mime_type).
    Raises ValueError on disallowed type or oversized file.
    """
    original = uploaded.name
    ext = Path(original).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(f"File type '{ext or '?'}' is not allowed.")

    data = uploaded.getbuffer()
    size = len(data)
    max_bytes = CONFIG.max_upload_mb * 1024 * 1024
    if size > max_bytes:
        raise ValueError(f"File exceeds {CONFIG.max_upload_mb} MB limit.")

    clean = _safe_name(original)
    stored = f"{uuid.uuid4().hex[:12]}_{clean}"
    dest = case_dir(case_number) / stored
    dest.write_bytes(bytes(data))
    return stored, original, size, getattr(uploaded, "type", None)


def attachment_path(case_number: str, stored_name: str) -> Path:
    return case_dir(case_number) / stored_name


def delete_attachment_file(case_number: str, stored_name: str) -> None:
    path = attachment_path(case_number, stored_name)
    if path.exists():
        path.unlink(missing_ok=True)
