"""
_status_manager.py — Reference implementation.

Place this file next to your automation script.
The automation writes status at each step; the dashboard reads it via /api/status.
"""
from __future__ import annotations
import json
import time
from pathlib import Path


DEFAULT_STATUS = {
    "status": "idle",          # idle | running | completed | error
    "current_step": "\u2014",
    "page": "\u2014",
    "topic": "\u2014",
    "project_folder": "\u2014",
    "project_dir": "\u2014",
    "progress_pct": 0,
    "last_update": "",
    "started_at": "",
}


class StatusManager:
    """Writer/reader pair around _status.json for live dashboard consumption."""

    def __init__(self, root: Path):
        self._path = root / "_status.json"
        self._root = root
        self._data = dict(DEFAULT_STATUS)
        self._write()

    # -- internal --

    def _now(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def _write(self) -> None:
        self._data["last_update"] = self._now()
        try:
            self._path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass  # best-effort

    # -- setters for automation to call --

    def set_status(self, status: str) -> None:
        self._data["status"] = status
        if status == "running" and not self._data["started_at"]:
            self._data["started_at"] = self._now()
        if status in ("completed", "error", "idle"):
            self._data["started_at"] = ""
        self._write()

    def set_step(self, step: str, progress: int | None = None) -> None:
        self._data["current_step"] = step
        if progress is not None:
            self._data["progress_pct"] = min(100, max(0, progress))
        self._write()

    def set_page(self, page: str) -> None:
        self._data["page"] = page
        self._write()

    def set_topic(self, topic: str) -> None:
        self._data["topic"] = topic
        self._write()

    def set_project(self, folder_name: str, directory: str) -> None:
        self._data["project_folder"] = folder_name
        self._data["project_dir"] = directory
        self._write()

    def mark_error(self, msg: str) -> None:
        self._data["status"] = "error"
        self._data["current_step"] = f"ERROR: {msg}"
        self._data["started_at"] = ""
        self._write()

    def mark_completed(self) -> None:
        self._data["status"] = "completed"
        self._data["progress_pct"] = 100
        self._data["started_at"] = ""
        self._write()

    # -- reader (called by dashboard server) --

    def read(self) -> dict:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return dict(DEFAULT_STATUS)

    @property
    def path(self) -> Path:
        return self._path
